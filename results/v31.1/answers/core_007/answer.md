# core_007 Answer

**Run**: 2
**Iterations**: 1

## Answer

# 插件化框架设计与实现

## 架构简图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Plugin Framework                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │   Plugin    │    │  Dependency │    │   HotSwap   │                  │
│  │  Manager    │◄──►│  Resolver   │◄──►│  Manager    │                  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                  │
│         │                  │                  │                         │
│         ▼                  ▼                  ▼                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │   Loader    │    │   Graph     │    │   Watcher   │                  │
│  │             │    │  Analyzer   │    │             │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                          Plugin Sandbox                                  │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐           │
│  │PluginA │  │PluginB │  │PluginC │  │PluginD │  │PluginE │           │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 核心代码实现

### 1. 依赖类型定义

```python
# plugin_framework/types.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Set, Optional, Callable, Any, Type
import asyncio
from datetime import datetime
import semver

class PluginState(Enum):
    """插件状态枚举"""
    UNLOADED = auto()
    LOADING = auto()
    LOADED = auto()
    ACTIVE = auto()
    DISABLING = auto()
    DISABLED = auto()
    ERROR = auto()
    UNINSTALLING = auto()

class LoadPriority(Enum):
    """加载优先级"""
    CRITICAL = 0      # 系统核心
    HIGH = 100        # 高优先级
    NORMAL = 200      # 普通优先级
    LOW = 300         # 低优先级
    ON_DEMAND = 400   # 按需加载

@dataclass
class Version:
    """语义化版本"""
    major: int = 0
    minor: int = 0
    patch: int = 0
    prerelease: str = ""
    
    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return base + (f"-{self.prerelease}" if self.prerelease else "")
    
    @classmethod
    def parse(cls, version_str: str) -> Version:
        """解析版本字符串"""
        # 处理 prerelease
        prerelease = ""
        if '-' in version_str:
            version_str, prerelease = version_str.split('-', 1)
        
        parts = version_str.split('.')
        return cls(
            major=int(parts[0]) if len(parts) > 0 else 0,
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0,
            prerelease=prerelease
        )
    
    def satisfies(self, constraint: str) -> bool:
        """检查版本是否满足约束"""
        return semver.match(str(self), constraint)
    
    def __lt__(self, other: Version) -> bool:
        return (self.major, self.minor, self.patch, self.prerelease) < \
               (other.major, other.minor, other.patch, other.prerelease)
    
    def __eq__(self, other: Version) -> bool:
        return (self.major, self.minor, self.patch, self.prerelease) == \
               (other.major, other.minor, other.patch, other.prerelease)

@dataclass
class Dependency:
    """插件依赖定义"""
    name: str
    version_constraint: str = ">=1.0.0"
    optional: bool = False
    description: str = ""
    
    def is_satisfied_by(self, version: Version) -> bool:
        """检查版本是否满足依赖约束"""
        return version.satisfies(self.version_constraint)

@dataclass
class PluginMetadata:
    """插件元数据"""
    id: str
    name: str
    version: Version
    description: str = ""
    author: str = ""
    homepage: str = ""
    dependencies: List[Dependency] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)  # 提供的服务
    load_priority: LoadPriority = LoadPriority.NORMAL
    tags: Set[str] = field(default_factory=set)
    entry_point: str = ""
    config_schema: Dict[str, Any] = field(default_factory=dict)
```

### 2. 依赖解析器

```python
# plugin_framework/dependency_resolver.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable
from enum import Enum, auto
import graphlib
from plugin_framework.types import PluginMetadata, Dependency, Version

class DependencyError(Exception):
    """依赖错误基类"""
    pass

class MissingDependencyError(DependencyError):
    """缺失依赖"""
    def __init__(self, plugin_id: str, dependency: Dependency):
        self.plugin_id = plugin_id
        self.dependency = dependency
        super().__init__(
            f"Plugin '{plugin_id}' requires '{dependency.name}' "
            f"with version {dependency.version_constraint}"
        )

class VersionConflictError(DependencyError):
    """版本冲突"""
    def __init__(self, plugin1: str, v1: Version, plugin2: str, v2: Version):
        self.plugin1 = plugin1
        self.v1 = v1
        self.plugin2 = plugin2
        self.v2 = v2
        super().__init__(
            f"Version conflict: {plugin1} requires {v1}, "
            f"{plugin2} requires {v2}"
        )

class CircularDependencyError(DependencyError):
    """循环依赖"""
    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        super().__init__(f"Circular dependency detected: {' -> '.join(cycle)}")

@dataclass
class ResolutionResult:
    """解析结果"""
    success: bool
    load_order: List[str] = field(default_factory=list)
    errors: List[DependencyError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_optional: List[Tuple[str, str]] = field(default_factory=list)

class DependencyResolver:
    """
    依赖解析器
    
    功能：
    - 依赖图构建
    - 拓扑排序
    - 循环依赖检测
    - 版本冲突检测
    - 缺失依赖识别
    """
    
    def __init__(self):
        self._plugins: Dict[str, PluginMetadata] = {}
        self._plugin_versions: Dict[str, Version] = {}  # 已安装版本
        self._satisfied_deps: Dict[str, Set[str]] = {}  # plugin -> 已满足的依赖
        
    def register_plugin(self, metadata: PluginMetadata) -> None:
        """注册插件"""
        self._plugins[metadata.id] = metadata
        self._plugin_versions[metadata.id] = metadata.version
        
    def unregister_plugin(self, plugin_id: str) -> None:
        """注销插件"""
        self._plugins.pop(plugin_id, None)
        self._plugin_versions.pop(plugin_id, None)
        self._satisfied_deps.pop(plugin_id, None)
        
    def resolve(self, target_plugins: Optional[List[str]] = None) -> ResolutionResult:
        """
        解析依赖关系
        
        Args:
            target_plugins: 目标插件列表，None 表示所有插件
            
        Returns:
            ResolutionResult: 解析结果
        """
        result = ResolutionResult(success=True)
        
        # 确定需要解析的插件
        plugins_to_resolve = target_plugins or list(self._plugins.keys())
        
        # 1. 构建依赖图
        dep_graph = self._build_dependency_graph(plugins_to_resolve)
        
        # 2. 检查缺失依赖
        self._check_missing_dependencies(plugins_to_resolve, result)
        
        # 3. 检查循环依赖
        cycles = self._detect_circular_dependencies(dep_graph)
        if cycles:
            result.errors.append(CircularDependencyError(cycles[0]))
            result.success = False
            
        # 4. 版本冲突检测
        self._check_version_conflicts(result)
        
        # 5. 拓扑排序确定加载顺序
        if result.success:
            load_order = self._topological_sort(plugins_to_resolve, dep_graph)
            result.load_order = load_order
            
        return result
    
    def _build_dependency_graph(self, plugins: List[str]) -> Dict[str, Set[str]]:
        """构建依赖图"""
        graph: Dict[str, Set[str]] = {p: set() for p in plugins}
        
        for plugin_id in plugins:
            if plugin_id not in self._plugins:
                continue
                
            metadata = self._plugins[plugin_id]
            for dep in metadata.dependencies:
                if dep.name in self._plugins:
                    graph[plugin_id].add(dep.name)
                elif not dep.optional:
                    # 可选依赖缺失不添加到图中
                    graph[plugin_id].add(dep.name)
                    
        return graph
    
    def _check_missing_dependencies(
        self, 
        plugins: List[str], 
        result: ResolutionResult
    ) -> None:
        """检查缺失的依赖"""
        satisfied: Dict[str, Set[str]] = {}
        
        for plugin_id in plugins:
            if plugin_id not in self._plugins:
                continue
                
            metadata = self._plugins[plugin_id]
            satisfied[plugin_id] = set()
            
            for dep in metadata.dependencies:
                dep_plugin = self._plugins.get(dep.name)
                
                if dep_plugin is None:
                    if dep.optional:
                        result.missing_optional.append((plugin_id, dep.name))
                    else:
                        result.errors.append(MissingDependencyError(plugin_id, dep))
                        result.success = False
                elif not dep.is_satisfied_by(dep_plugin.version):
                    result.errors.append(
                        MissingDependencyError(plugin_id, dep)
                    )
                    result.success = False
                else:
                    satisfied[plugin_id].add(dep.name)
                    
        self._satisfied_deps = satisfied
    
    def _detect_circular_dependencies(
        self, 
        graph: Dict[str, Set[str]]
    ) -> List[List[str]]:
        """检测循环依赖"""
        cycles = []
        
        def dfs(node: str, path: List[str], visited: Set[str]) -> bool:
            if node in path:
                # 发现循环
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
                
            if node in visited:
                return False
                
            visited.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor in graph:  # 只检查已注册的依赖
                    dfs(neighbor, path, visited)
                    
            path.pop()
            return False
            
        visited = set()
        for node in graph:
            if node not in visited:
                dfs(node, [], visited)
                
        return cycles
    
    def _check_version_conflicts(self, result: ResolutionResult) -> None:
        """检查版本冲突"""
        # 简化实现：检查是否有同一插件的不同版本要求
        version_requirements: Dict[str, List[Tuple[str, str]]] = {}
        
        for plugin_id, metadata in self._plugins.items():
            for dep in metadata.dependencies:
                if dep.name not in version_requirements:
                    version_requirements[dep.name] = []
                version_requirements[dep.name].append(
                    (plugin_id, dep.version_constraint)
                )
                
        # 这里可以添加更复杂的版本冲突检测逻辑
        # 当前实现依赖 semver 库处理
        
    def _topological_sort(
        self, 
        plugins: List[str], 
        graph: Dict[str, Set[str]]
    ) -> List[str]:
        """拓扑排序获取加载顺序"""
        # 使用 Kahn 算法
        in_degree = {p: 0 for p in plugins}
        
        for plugin in plugins:
            for dep in graph.get(plugin, set()):
                if dep in in_degree:
                    in_degree[plugin] += 1
                    
        queue = [p for p, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # 按优先级排序
            queue.sort(key=lambda p: self._plugins[p].load_priority.value)
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in plugins:
                if node in graph.get(neighbor, set()):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
                        
        return result
    
    def get_load_order(self, plugin_ids: List[str]) -> List[str]:
        """获取插件加载顺序"""
        result = self.resolve(plugin_ids)
        return result.load_order
```

### 3. 插件基类和接口

```python
# plugin_framework/plugin.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Set, List, TYPE_CHECKING
from dataclasses import dataclass, field
import asyncio
from datetime import datetime
import logging

if TYPE_CHECKING:
    from plugin_framework.manager import PluginManager

logger = logging.getLogger(__name__)

@dataclass
class PluginContext:
    """插件上下文"""
    plugin_id: str
    config: Dict[str, Any] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    event_bus: Optional[Any] = None
    resource_limits: Dict[str, Any] = field(default_factory=dict)

class PluginBase(ABC):
    """
    插件基类
    
    所有插件必须继承此类并实现相应接口
    """
    
    # 类级别元数据
    metadata: Optional[PluginMetadata] = None
    
    def __init__(self):
        self._context: Optional[PluginContext] = None
        self._state: str = "initialized"
        self._loaded_at: Optional[datetime] = None
        self._error: Optional[Exception] = None
        
    @property
    def context(self) -> PluginContext:
        """获取插件上下文"""
        if self._context is None:
            raise RuntimeError("Plugin context not set")
        return self._context
    
    @property
    def plugin_id(self) -> str:
        """获取插件ID"""
        return self.context.plugin_id
    
    @property
    def state(self) -> str:
        """获取插件状态"""
        return self._state
        
    def initialize(self, context: PluginContext) -> None:
        """初始化插件"""
        self._context = context
        self._state = "initialized"
        logger.info(f"Plugin {self.plugin_id} initialized")
        
    @abstractmethod
    async def on_load(self) -> None:
        """插件加载时调用"""
        pass
    
    @abstractmethod
    async def on_enable(self) -> None:
        """插件启用时调用"""
        pass
    
    @abstractmethod
    async def on_disable(self) -> None:
        """插件禁用时调用"""
        pass
    
    async def on_unload(self) -> None:
        """插件卸载时调用"""
        self._state = "unloaded"
        logger.info(f"Plugin {self.plugin_id} unloaded")
        
    async def on_update(self, old_version: str, new_version: str) -> bool:
        """
        插件更新时调用
        
        返回:
            True: 更新成功
            False: 需要完全重启
        """
        return True
        
    async def on_health_check(self) -> bool:
        """健康检查"""
        return self._state == "active"
        
    def get_api(self) -> Optional[Any]:
        """获取插件提供的 API"""
        return None
        
    def get_hooks(self) -> Dict[str, Callable]:
        """获取插件钩子"""
        return {}
```

### 4. 插件管理器

```python
# plugin_framework/manager.py
from __future__ import annotations
from typing import Dict, List, Optional, Set, Type, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import asyncio
import importlib
import importlib.util
import sys
import os
import hashlib
import json
from pathlib import Path
from datetime import datetime
import logging

from plugin_framework.types import (
    PluginState, PluginMetadata, Version, Dependency, LoadPriority
)
from plugin_framework.dependency_resolver import DependencyResolver, ResolutionResult
from plugin_framework.plugin import PluginBase, PluginContext
from plugin_framework.hot_swap import HotSwapManager, UpdateInfo

logger = logging.getLogger(__name__)

@dataclass
class PluginInstance:
    """插件实例"""
    metadata: PluginMetadata
    instance: PluginBase
    state: PluginState = PluginState.UNLOADED
    loaded_at: Optional[datetime] = None
    enabled_at: Optional[datetime] = None
    error: Optional[str] = None
    checksum: Optional[str] = None
    
class PluginManager:
    """
    插件管理器
    
    核心功能：
    - 插件注册/注销
    - 插件加载/卸载
    - 插件启用/禁用
    - 生命周期管理
    - 事件分发
    """
    
    def __init__(self, plugin_dir: str = "./plugins"):
        self.plugin_dir = Path(plugin_dir)
        self._plugins: Dict[str, PluginInstance] = {}
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        self._hooks: Dict[str, List[Callable]] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._shared_services: Dict[str, Any] = {}
        
        self._dep_resolver = DependencyResolver()
        self._hot_swap_manager = HotSwapManager(self)
        
        self._lock = asyncio.Lock()
        self._initialized = False
        
    async def initialize(self) -> None:
        """初始化管理器"""
        if self._initialized:
            return
            
        # 确保插件目录存在
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # 扫描并加载插件
        await self._scan_plugins()
        
        # 解析依赖并确定加载顺序
        await self._resolve_and_load()
        
        self._initialized = True
        logger.info(f"PluginManager initialized with {len(self._plugins)} plugins")
        
    async def _scan_plugins(self) -> None:
        """扫描插件目录"""
        for item in self.plugin_dir.iterdir():
            if item.is_file() and item.suffix == '.py':
                await self._load_plugin_module(item)
            elif item.is_dir() and (item / '__init__.py').exists():
                await self._load_plugin_module(item)
                
    async def _load_plugin_module(self, path: Path) -> None:
        """加载插件模块"""
        try:
            module_name = path.stem if path.is_file() else path.name
            spec = importlib.util.spec_from_file_location(
                module_name, 
                path / '__init__.py' if path.is_dir() else path
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # 查找插件类
                for name in dir(module):
                    obj = getattr(module, name)
                    if (isinstance(obj, type) and 
                        issubclass(obj, PluginBase) and 
                        obj != PluginBase and
                        hasattr(obj, 'metadata') and
                        obj.metadata is not None):
                        
                        self._plugin_classes[obj.metadata.id] = obj
                        self._dep_resolver.register_plugin(obj.metadata)
                        logger.info(f"Discovered plugin: {obj.metadata.id}")
                        
        except Exception as e:
            logger.error(f"Failed to load plugin from {path}: {e}")
            
    async def _resolve_and_load(self) -> None:
        """解析依赖并加载插件"""
        result = self._dep_resolver.resolve()
        
        if not result.success:
            for error in result.errors:
                logger.error(f"Dependency error: {error}")
            return
            
        # 按顺序加载插件
        for plugin_id in result.load_order:
            if plugin_id in self._plugin_classes:
                await self._load_plugin(plugin_id)
                
    async def _load_plugin(self, plugin_id: str) -> None:
        """加载单个插件"""
        async with self._lock:
            if plugin_id in self._plugins:
               
