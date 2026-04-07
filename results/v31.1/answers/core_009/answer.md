# core_009 Answer

**Run**: 2
**Iterations**: 1

## Answer

# 简化版 Raft 共识算法实现

## 架构简图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Raft 集群架构                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│   │ Node 1  │     │ Node 2  │     │ Node 3  │     │ Node 4  │     │ Node 5  │
│   │ (Leader)│◄───►│(Follower)│◄───►│(Follower)│◄───►│(Follower)│◄───►│(Follower)│
│   └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
│        │               │               │               │               │
│        └───────────────┴───────────────┴───────────────┴───────────────┘
│                                    │                                     
│                         ┌──────────┴──────────┐                         
│                         │   状态机 (State)     │                         
│                         │   日志 (Log)         │                         
│                         │   持久化存储         │                         
│                         └─────────────────────┘                         
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                           核心数据结构                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  Term:      任期号（单调递增）                                            │
│  VoteCount: 获得的票数                                                    │
│  Log:       日志条目列表 [term, command]                                  │
│  CommitIdx: 已提交的日志索引                                              │
│  LastIdx:   最后日志索引                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

## 核心代码实现

```python
#!/usr/bin/env python3
"""
简化版 Raft 共识算法实现
包含 Leader 选举和日志复制
"""

import asyncio
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set
import copy


# ============================================================================
# 数据结构定义
# ============================================================================

class NodeState(Enum):
    """节点状态"""
    FOLLOWER = auto()
    CANDIDATE = auto()
    LEADER = auto()


@dataclass
class LogEntry:
    """日志条目"""
    term: int          # 日志条目时的任期号
    command: any       # 状态机命令
    index: int = 0     # 日志索引
    
    def __repr__(self):
        return f"LogEntry(term={self.term}, index={self.index}, command={self.command})"


@dataclass
class RequestVoteArgs:
    """RequestVote RPC 参数"""
    term: int           # 候选人的任期号
    candidate_id: int   # 候选人 ID
    last_log_index: int # 候选人最后日志条目的索引
    last_log_term: int  # 候选人最后日志条目的任期号


@dataclass
class RequestVoteReply:
    """RequestVote RPC 响应"""
    term: int          # 当前任期号
    vote_granted: bool # 是否投票给该候选人


@dataclass
class AppendEntriesArgs:
    """AppendEntries RPC 参数"""
    term: int           # 领导者的任期号
    leader_id: int      # 领导者 ID
    prev_log_index: int # 日志条目之前的索引
    prev_log_term: int  # prev_log_index 条目的任期号
    entries: List[LogEntry]  # 需要追加的日志条目
    leader_commit: int  # 领导者的 commitIndex


@dataclass
class AppendEntriesReply:
    """AppendEntries RPC 响应"""
    term: int           # 当前任期号
    success: bool       # 是否成功
    match_index: int    # 匹配的日志索引
    last_index: int     # 最后日志索引


# ============================================================================
# Raft 节点实现
# ============================================================================

class RaftNode:
    """Raft 节点实现"""
    
    def __init__(
        self,
        node_id: int,
        peers: List[int],
        election_timeout_range: tuple = (150, 300),
        heartbeat_interval: float = 50,
        storage=None
    ):
        self.node_id = node_id
        self.peers = peers  # 其他节点 ID 列表
        
        # 超时配置（毫秒）
        self.election_timeout_range = election_timeout_range
        self.heartbeat_interval = heartbeat_interval  # 毫秒
        
        # 持久化状态（简化版存内存，生产环境需要持久化）
        self.current_term = 0
        self.voted_for: Optional[int] = None
        self.log: List[LogEntry] = []
        
        # Volatile 状态
        self.state = NodeState.FOLLOWER
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader 专用状态
        self.next_index: Dict[int, int] = {}  # 每个节点的下一条日志索引
        self.match_index: Dict[int, int] = {}  # 每个节点已复制的最高日志索引
        
        # 选举计时器
        self.last_received_time = time.time() * 1000  # 毫秒
        self.election_timeout = self._random_election_timeout()
        
        # 网络层（简化实现）
        self.transport: Optional['Transport'] = None
        
        # 状态机
        self.state_machine = StateMachine()
        
        # 锁
        self._lock = asyncio.Lock()
        
        # 任务
        self._tasks: List[asyncio.Task] = []
        
        # 日志
        self._logger = Logger(node_id)
        
        # 统计
        self.stats = {
            'election_count': 0,
            'vote_count': 0,
            'append_count': 0,
            'commit_count': 0
        }
    
    def _random_election_timeout(self) -> float:
        """生成随机选举超时时间"""
        return random.uniform(*self.election_timeout_range)
    
    # ========================================================================
    # RPC 处理
    # ========================================================================
    
    async def handle_request_vote(self, args: RequestVoteArgs) -> RequestVoteReply:
        """处理 RequestVote RPC"""
        async with self._lock:
            self._logger.log(f"收到 RequestVote from {args.candidate_id}, term={args.term}")
            
            # 1. 如果 term < currentTerm，拒绝投票
            if args.term < self.current_term:
                return RequestVoteReply(term=self.current_term, vote_granted=False)
            
            # 2. 如果 term > currentTerm，更新 term，变为 Follower
            if args.term > self.current_term:
                self._become_follower(args.term)
            
            # 3. 判断是否可以投票
            can_vote = (
                self.voted_for is None or 
                self.voted_for == args.candidate_id
            )
            
            # 4. 判断候选人日志是否至少和本地日志一样新
            last_log_term = self._get_last_log_term()
            last_log_index = self._get_last_log_index()
            
            log_ok = (
                args.last_log_term > last_log_term or
                (args.last_log_term == last_log_term and 
                 args.last_log_index >= last_log_index)
            )
            
            # 5. 如果满足条件，投票
            if can_vote and log_ok:
                self.voted_for = args.candidate_id
                self.last_received_time = time.time() * 1000
                self._logger.log(f"投票给 {args.candidate_id}")
                return RequestVoteReply(term=self.current_term, vote_granted=True)
            
            return RequestVoteReply(term=self.current_term, vote_granted=False)
    
    async def handle_append_entries(self, args: AppendEntriesArgs) -> AppendEntriesReply:
        """处理 AppendEntries RPC"""
        async with self._lock:
            self._logger.log(
                f"收到 AppendEntries from {args.leader_id}, "
                f"term={args.term}, prev_idx={args.prev_log_index}"
            )
            
            # 1. 如果 term < currentTerm，返回 false
            if args.term < self.current_term:
                return AppendEntriesReply(
                    term=self.current_term, 
                    success=False,
                    match_index=0,
                    last_index=self._get_last_log_index()
                )
            
            # 2. 更新 term，可能需要变为 Follower
            if args.term > self.current_term:
                self._become_follower(args.term)
            
            # 3. 重置选举超时
            self.last_received_time = time.time() * 1000
            
            # 4. 如果 prevLogIndex 在本地不存在，返回 false
            if args.prev_log_index > 0:
                if args.prev_log_index > self._get_last_log_index():
                    return AppendEntriesReply(
                        term=self.current_term,
                        success=False,
                        match_index=0,
                        last_index=self._get_last_log_index()
                    )
                
                # 检查 prevLogIndex 处的日志 term 是否匹配
                if args.prev_log_index <= len(self.log):
                    local_term = self.log[args.prev_log_index - 1].term
                    if local_term != args.prev_log_term:
                        # 日志冲突，删除该条目及之后的所有条目
                        self.log = self.log[:args.prev_log_index - 1]
                        return AppendEntriesReply(
                            term=self.current_term,
                            success=False,
                            match_index=0,
                            last_index=self._get_last_log_index()
                        )
            
            # 5. 追加新的日志条目
            for i, entry in enumerate(args.entries):
                log_index = args.prev_log_index + 1 + i
                
                # 如果已存在的日志条目与新条目冲突，删除并替换
                if log_index <= len(self.log):
                    if self.log[log_index - 1].term != entry.term:
                        self.log = self.log[:log_index - 1]
                        self.log.append(entry)
                else:
                    self.log.append(entry)
            
            # 6. 如果 leaderCommit > commitIndex，更新 commitIndex
            if args.leader_commit > self.commit_index:
                self.commit_index = min(args.leader_commit, self._get_last_log_index())
            
            # 7. 应用日志到状态机
            await self._apply_to_state_machine()
            
            return AppendEntriesReply(
                term=self.current_term,
                success=True,
                match_index=args.prev_log_index + len(args.entries),
                last_index=self._get_last_log_index()
            )
    
    # ========================================================================
    # 状态转换
    # ========================================================================
    
    def _become_follower(self, term: int):
        """变为 Follower"""
        self.state = NodeState.FOLLOWER
        self.current_term = term
        self.voted_for = None
        self._logger.log(f"变为 Follower, term={term}")
    
    def _become_candidate(self):
        """变为 Candidate，发起选举"""
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.stats['election_count'] += 1
        self._logger.log(f"变为 Candidate, term={self.current_term}")
    
    def _become_leader(self):
        """变为 Leader"""
        self.state = NodeState.LEADER
        self._logger.log(f"变为 Leader, term={self.current_term}")
        
        # 初始化 nextIndex 和 matchIndex
        last_index = self._get_last_log_index()
        for peer_id in self.peers:
            self.next_index[peer_id] = last_index + 1
            self.match_index[peer_id] = 0
    
    # ========================================================================
    # 选举逻辑
    # ========================================================================
    
    async def start_election(self):
        """开始一次选举"""
        async with self._lock:
            self._become_candidate()
            current_term = self.current_term
            last_log_index = self._get_last_log_index()
            last_log_term = self._get_last_log_term()
        
        # 收集选票
        vote_count = 1  # 投自己一票
        
        async with self._lock:
            # 发送 RequestVote 到所有节点
            for peer_id in self.peers:
                asyncio.create_task(self._send_request_vote(peer_id, current_term, last_log_index, last_log_term))
    
    async def _send_request_vote(self, peer_id: int, term: int, last_log_index: int, last_log_term: int):
        """发送 RequestVote RPC"""
        args = RequestVoteArgs(
            term=term,
            candidate_id=self.node_id,
            last_log_index=last_log_index,
            last_log_term=last_log_term
        )
        
        try:
            if self.transport:
                reply = await self.transport.send_request_vote(peer_id, args)
                await self._handle_vote_reply(reply)
        except Exception as e:
            self._logger.log(f"发送 RequestVote 到 {peer_id} 失败: {e}")
    
    async def _handle_vote_reply(self, reply: RequestVoteReply):
        """处理投票回复"""
        async with self._lock:
            # 忽略来自旧 term 的回复
            if reply.term != self.current_term:
                return
            
            if reply.vote_granted:
                self.stats['vote_count'] += 1
                vote_count = self.stats['vote_count']
                
                # 获得多数票，成为 Leader
                if vote_count > (len(self.peers) + 1) // 2:
                    self._become_leader()
                    
                    # 成为 Leader 后立即发送心跳
                    await self._send_heartbeats()
    
    # ========================================================================
    # 日志复制逻辑
    # ========================================================================
    
    async def start_replication(self, command):
        """开始复制日志（仅 Leader）"""
        if self.state != NodeState.LEADER:
            return False
        
        async with self._lock:
            # 追加日志条目
            entry = LogEntry(
                term=self.current_term,
                command=command,
                index=len(self.log) + 1
            )
            self.log.append(entry)
            
            # 并行复制到所有节点
            for peer_id in self.peers:
                asyncio.create_task(self._replicate_to_peer(peer_id))
            
            return True
    
    async def _replicate_to_peer(self, peer_id: int):
        """复制日志到指定节点"""
        async with self._lock:
            if self.state != NodeState.LEADER:
                return
            
            next_idx = self.next_index[peer_id]
            
            # 构造 AppendEntries RPC
            if next_idx <= len(self.log):
                # 有日志需要复制
                prev_log_index = next_idx - 1
                prev_log_term = self.log[prev_log_index - 1].term if prev_log_index > 0 else 0
                entries = self.log[prev_log_index:]
            else:
                # 没有日志需要复制，发送心跳
                prev_log_index = len(self.log)
                prev_log_term = self._get_last_log_term()
                entries = []
            
            args = AppendEntriesArgs(
                term=self.current_term,
                leader_id=self.node_id,
                prev_log_index=prev_log_index,
                prev_log_term=prev_log_term,
                entries=entries,
                leader_commit=self.commit_index
            )
        
        try:
            if self.transport:
                reply = await self.transport.send_append_entries(peer_id, args)
                await self._handle_append_reply(peer_id, reply)
        except Exception as e:
            self._logger.log(f"复制日志到 {peer_id} 失败: {e}")
    
    async def _handle_append_reply(self, peer_id: int, reply: AppendEntriesReply):
        """处理 AppendEntries 回复"""
        async with self._lock:
            if reply.term != self.current_term:
                return
            
            if reply.success:
                # 更新 matchIndex 和 nextIndex
                self.match_index[peer_id] = reply.match_index
                self.next_index[peer_id] = reply.match_index + 1
                
                # 检查是否可以提交
                await self._try_commit()
            else:
                # 递减 nextIndex 重试
                self.next_index[peer_id] = max(1, self.next_index[peer_id] - 1)
                # 重试复制
                asyncio.create_task(self._replicate_to_peer(peer_id))
    
    async def _try_commit(self):
        """尝试提交日志"""
        if self.state != NodeState.LEADER:
            return
        
        # 统计有多少节点已经复制了该日志
        n = len(self.peers) + 1  # 总节点数
        majority = n // 2
        
        for index in range(self.commit_index + 1, len(self.log) + 1):
            count = 1  # Leader 自身
            for peer_id in self.peers:
                if self.match_index[peer_id] >= index:
                    count += 1
            
            if count > majority:
                # 找到多数，可以提交
                if self.log[index - 1].term == self.current_term:
                    self.commit_index = index
                    self.stats['commit_count'] += 1
                    self._logger.log(f"提交日志 index={index}")
                    await self._apply_to_state_machine()
    
    async def _apply_to_state_machine(self):
        """应用日志到状态机"""
        while self.commit_index > self.last_applied:
            self.last_applied += 1
            entry = self.log[self.last_applied - 1]
            self.state_machine.apply(entry.command)
            self._logger.log(f"应用日志 index={entry.index}, command={entry.command}")
    
    async def _send_heartbeats(self):
        """发送心跳"""
        if self.state != NodeState.LEADER:
            return
        
        async with self._lock:
            args = AppendEntriesArgs(
                term=self.current_term,
                leader_id=self.node_id,
                prev_log_index=self._get_last_log_index(),
                prev_log_term=self._get_last_log_term(),
                entries=[],  # 心跳不携带日志
                leader_commit=self.commit_index
            )
        
        for peer_id in self.peers:
            try:
                if self.transport:
                    asyncio.create_task(self.transport.send_append_entries(peer_id, args))
            except Exception as e:
                self._logger.log(f"发送心跳到 {peer_id} 失败: {e}")
    
    # ========================================================================
    # 辅助方法
    # ========================================================================
    
    def _get_last_log_index(self) -> int:
        """获取最后日志索引"""
        if self.log:
            return self.log[-1].index
        return 0
    
    def _get_last_log_term(self) -> int:
        """获取最后日志任期"""
        if self.log:
            return self.log[-1].term
        return 0
    
    # ========================================================================
    # 运行循环
    # ========================================================================
    
    async def run(self):
        """运行节点主循环"""
        self._tasks.append(asyncio.create_task(self._election_timer_loop()))
        self._tasks.append(asyncio.create_task(self._leader_heartbeat_loop()))
    
    async def _election_timer_loop(self):
        """选举计时器循环"""
        while True:
            await asyncio.sleep(0.01)  # 10ms 检查一次
            
            current_time = time.time() * 1000
            elapsed = current_time - self.last_received_time
            
            if elapsed >= self.election_timeout:
                async with self._lock:
                    if self.state != NodeState.LEADER:
                        self.election_timeout = self._random_election_timeout()
                        self.last_received_time = current_time
                
                # 发起选举
                await self.start_election()
    
    async def _leader_heartbeat_loop(self):
        """Leader 心跳循环"""
        while True:
            await asyncio.sleep(self.heartbeat_interval / 1000)  # 转换为秒
            
            async with self._lock:
                if self.state == NodeState.LEADER:
                    await self._send_heartbeats()
    
    async def stop(self):
        """停止节点"""
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()


# ============================================================================
# 状态机
# ============================================================================

class StateMachine:
    """简单的状态机实现"""
    
    def __init__(self):
        self.state: Dict[str, any] = {}
    
    def apply(self, command):
        """应用命令"""
        if isinstance(command, dict):
            op = command.get('op')
            key = command.get('key')
            value = command.get('value')
            
            if op == 'set':
                self.state[key] = value
            elif op == 'delete':
                self.state.pop(key, None)
        return self.state.copy()


# ============================================================================
# 网络传输层
# ============================================================================

class Transport:
    """网络传输层（简化实现，使用进程内消息传递）"""
    
    def __init__(self):
        self.nodes: Dict[int, RaftNode] = {}
        self._latency_range = (5, 20)  # 模拟网络延迟（毫秒）
    
    def register_node(self, node: RaftNode):
        """注册节点"""
        node.transport = self
        self.nodes[node.node_id] = node
    
    async def send_request_vote(self, target_id: int, args: RequestVoteArgs) -> RequestVoteReply:
        """发送 RequestVote RPC"""
        # 模拟网络延迟
        await asyncio.sleep(random.uniform(*self._latency_range) / 1000)
        
        target = self.nodes.get(target_id)
        if target:
            return await target.handle_request_vote(args)
        raise ConnectionError(f"节点 {target_id} 不存在")
    
    async def send_append_entries(self, target_id: int, args: AppendEntriesArgs) -> AppendEntriesReply:
        """发送 AppendEntries RPC"""
        # 模拟网络延迟
        await asyncio.sleep(random.uniform(*self._latency_range) / 1000)
        
        target = self.nodes.get(target_id)
        if target:
            return await target.handle_append_entries(args)
        raise ConnectionError(f"节点 {target_id} 不存在")


# ============================================================================
# 日志系统
# ============================================================================

class Logger:
    """简单的日志系统"""
    
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.logs: List[str] = []
    
    def log(self, message:
