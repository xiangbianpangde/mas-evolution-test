# gen_002 Answer

**Run**: 1
**Iterations**: 1

## Answer

# 联邦学习梯度聚合算法实现

## 1. 架构简图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          联邦学习梯度聚合架构                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐             │
│    │Client 1 │     │Client 2 │     │Client 3 │     │Client n │             │
│    │┌───────┐│     │┌───────┐│     │┌───────┐│     │┌───────┐│             │
│    ││Local   ││     ││Local   ││     ││Local   ││     ││Local   ││             │
│    ││Trainer ││     ││Trainer ││     ││Trainer ││     ││Trainer ││             │
│    │└───────┘│     │└───────┘│     │└───────┘│     │└───────┘│             │
│    │┌───────┐│     │┌───────┐│     │┌───────┐│     │┌───────┐│             │
│    ││Gradients│    ││Gradients│    ││Gradients│    ││Gradients│             │
│    │└───────┘│     │└───────┘│     │└───────┘│     │└───────┘│             │
│    └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘             │
│         │               │               │               │                   │
│         └───────────────┼───────────────┼───────────────┘                   │
│                         ▼                                               │
│              ┌─────────────────────┐                                      │
│              │   通信加密层         │                                      │
│              │  (TLS/同态加密)      │                                      │
│              └──────────┬──────────┘                                      │
│                         ▼                                               │
│    ╔═══════════════════════════════════════════════════════════════╗      │
│    ║                    聚合服务器                                  ║      │
│    ║  ┌─────────────────────────────────────────────────────────┐  ║      │
│    ║  │                    聚合策略选择器                         │  ║      │
│    ║  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │  ║      │
│    ║  │  │ FedAvg  │ │FedProx  │ │ Krum    │ │Trimmed  │ ...    │  ║      │
│    ║  │  │         │ │         │ │         │ │Mean     │        │  ║      │
│    ║  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │  ║      │
│    ║  └─────────────────────────────────────────────────────────┘  ║      │
│    ║                           │                                     ║      │
│    ║                           ▼                                     ║      │
│    ║  ┌─────────────────────────────────────────────────────────┐  ║      │
│    ║  │              聚合核心引擎                                 │  ║      │
│    ║  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  ║      │
│    ║  │  │ 加权平均器   │  │ 异常检测器   │  │ 差分隐私模块 │      │  ║      │
│    ║  │  │(WeightedAvg)│  │(Outlier)   │  │(DP Noise)  │      │  ║      │
│    ║  │  └─────────────┘  └─────────────┘  └─────────────┘      │  ║      │
│    ║  └─────────────────────────────────────────────────────────┘  ║      │
│    ╚═══════════════════════════════════════════════════════════════╝      │
│                                    │                                       │
│                                    ▼                                       │
│                         ┌─────────────────┐                                │
│                         │   全局模型更新   │                                │
│                         └─────────────────┘                                │
│                                                                             │
│    ┌──────────────────────────────────────────────────────────────────┐     │
│    │                         监控与日志                                │     │
│    │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │     │
│    │  │Round   │ │Accuracy│ │Loss    │ │Grad    │ │Privacy │        │     │
│    │  │Tracker │ │Monitor │ │Logger  │ │Norm    │ │Budget  │        │     │
│    │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │     │
│    └──────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘

聚合流程时序图:
────────────────────────────────────────────────────────────────────────────
Round t Start
     │
     ▼
Server ──广播全局模型──▶ Client 1, 2, 3, ..., n
     │
     │  ┌─ 本地训练 (E epochs) ─┐
     │  │                       │
     ▼  ▼                       │
Client i: 计算梯度 Δwᵢ        │
     │                       │
     └───────────────────────┘
     │
     ▼
Server ◀──上传梯度/模型更新── Client 1, 2, 3, ..., n
     │
     ▼
┌─────────────────────────────────────────┐
│          梯度聚合 (Aggregation)          │
│  ┌─────────────────────────────────────┐│
│  │ 1. 验证更新                          ││
│  │ 2. 异常检测 (可选)                    ││
│  │ 3. 加权聚合: Δw = Σ(nᵢ/n) × Δwᵢ     ││
│  │ 4. 差分隐私 (可选)                    ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
     │
     ▼
Server: 更新全局模型 w ← w + Δw
     │
     ▼
Round t End ──▶ Round t+1 Start
────────────────────────────────────────────────────────────────────────────
```

---

## 2. 核心代码（完整可运行）

### 2.1 项目结构

```
federated_learning/
├── core/
│   ├── __init__.py
│   ├── aggregation.py          # 聚合核心算法
│   ├── strategies.py           # 聚合策略实现
│   ├── client.py               # 客户端实现
│   ├── server.py               # 服务器实现
│   └── models.py               # 简单模型定义
├── utils/
│   ├── __init__.py
│   ├── privacy.py              # 差分隐私
│   ├── crypto.py               # 加密工具
│   └── metrics.py              # 指标计算
├── config/
│   └── default_config.py       # 默认配置
├── main.py                     # 主程序入口
├── test_aggregation.py         # 单元测试
└── simulation.py               # 模拟仿真
```

### 2.2 核心代码实现

```python
# ============================================================================
# 文件: federated_learning/core/aggregation.py
# 联邦学习梯度聚合核心实现
# ============================================================================

"""
联邦学习梯度聚合算法实现

包含多种聚合策略:
1. FedAvg (Federated Averaging) - McMahan et al., 2017
2. FedProx - Li et al., 2020
3. Krum - Blanchard et al., 2017
4. Trimmed Mean - Li et al., 2019
5. Median - Yin et al., 2018
"""

from __future__ import annotations
import numpy as np
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging
import hashlib
import hmac

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AggregationStrategy(Enum):
    """聚合策略枚举"""
    FEDAVG = "fedavg"
    FEDPROX = "fedprox"
    KRUM = "krum"
    TRIMMED_MEAN = "trimmed_mean"
    MEDIAN = "median"
    WEIGHTED_MEDIAN = "weighted_median"
    GEO_MEAN = "geometric_mean"


@dataclass
class ClientUpdate:
    """客户端更新数据结构"""
    client_id: str
    model_update: np.ndarray          # 模型参数更新 ( flattened )
    sample_size: int                  # 训练样本数量
    num_epochs: int                   # 本地训练轮数
    learning_rate: float              # 学习率
    timestamp: float                  # 时间戳
    gradient_norm: float = 0.0        # 梯度范数 (用于异常检测)
    validation_accuracy: float = 0.0  # 验证准确率
    
    # 认证和完整性
    client_signature: Optional[bytes] = None
    mac_keys: Optional[Dict[str, bytes]] = None  # 用于安全聚合
    
    def __post_init__(self):
        """计算梯度范数"""
        if self.gradient_norm == 0.0 and self.model_update.size > 0:
            self.gradient_norm = np.linalg.norm(self.model_update)
    
    @property
    def weight(self) -> float:
        """计算客户端权重 (基于样本数量)"""
        return self.sample_size


@dataclass
class AggregationResult:
    """聚合结果"""
    aggregated_update: np.ndarray
    strategy: str
    num_clients: int
    total_samples: int
    elapsed_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 质量指标
    avg_gradient_norm: float = 0.0
    max_gradient_norm: float = 0.0
    min_gradient_norm: float = 0.0
    std_gradient_norm: float = 0.0
    
    # 异常检测信息
    outliers_detected: List[int] = field(default_factory=list)
    outlier_scores: Optional[np.ndarray] = None


class BaseAggregator(ABC):
    """聚合器基类"""
    
    def __init__(
        self,
        num_byzantine: int = 0,
        min_clients: int = 2,
        timeout: float = 30.0,
        validate_updates: bool = True,
        max_gradient_norm: float = 100.0
    ):
        self.num_byzantine = num_byzantine
        self.min_clients = min_clients
        self.timeout = timeout
        self.validate_updates = validate_updates
        self.max_gradient_norm = max_gradient_norm
        
        # 统计信息
        self.total_aggregations = 0
        self.total_outliers = 0
    
    @abstractmethod
    def aggregate(
        self,
        updates: List[ClientUpdate],
        current_model: Optional[np.ndarray] = None,
        **kwargs
    ) -> AggregationResult:
        """执行聚合"""
        pass
    
    def validate_update(self, update: ClientUpdate) -> bool:
        """验证更新合法性"""
        if update.gradient_norm > self.max_gradient_norm:
            logger.warning(
                f"Client {update.client_id}: gradient norm {update.gradient_norm:.2f} "
                f"exceeds threshold {self.max_gradient_norm:.2f}"
            )
            return False
        
        if np.any(np.isnan(update.model_update)) or np.any(np.isinf(update.model_update)):
            logger.warning(f"Client {update.client_id}: contains NaN or Inf values")
            return False
        
        return True
    
    def compute_weights(self, updates: List[ClientUpdate]) -> np.ndarray:
        """计算归一化权重"""
        total_samples = sum(u.sample_size for u in updates)
        if total_samples == 0:
            return np.ones(len(updates)) / len(updates)
        return np.array([u.sample_size / total_samples for u in updates])


class FedAvgAggregator(BaseAggregator):
    """
    FedAvg (Federated Averaging) 聚合器
    
    论文: "Communication-Efficient Learning of Deep Networks from 
           Decentralized Data" (McMahan et al., 2017)
    
    聚合公式:
        Δw = Σᵢ (nᵢ / n) · Δwᵢ
    
    其中 nᵢ 是客户端 i 的样本数, n 是总样本数
    """
    
    def __init__(
        self,
        momentum: float = 0.0,
        server_momentum: float = 0.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.momentum = momentum
        self.server_momentum = server_momentum
        self._velocity = None
    
    def aggregate(
        self,
        updates: List[ClientUpdate],
        current_model: Optional[np.ndarray] = None,
        **kwargs
    ) -> AggregationResult:
        """执行 FedAvg 聚合"""
        import time
        start_time = time.time()
        
        # 验证客户端数量
        if len(updates) < self.min_clients:
            raise ValueError(
                f"Need at least {self.min_clients} clients, got {len(updates)}"
            )
        
        # 过滤无效更新
        valid_updates = []
        for update in updates:
            if self.validate_updates and not self.validate_update(update):
                continue
            valid_updates.append(update)
        
        if len(valid_updates) < self.min_clients:
            raise ValueError(
                f"Need at least {self.min_clients} valid updates, got {len(valid_updates)}"
            )
        
        # 计算权重
        weights = self.compute_weights(valid_updates)
        
        # 加权平均
        aggregated = np.zeros_like(valid_updates[0].model_update)
        for update, w in zip(valid_updates, weights):
            aggregated += w * update.model_update
        
        # 应用服务器动量
        if self.server_momentum > 0:
            if self._velocity is None:
                self._velocity = aggregated.copy()
            else:
                self._velocity = (
                    self.server_momentum * self._velocity +
                    (1 - self.server_momentum) * aggregated
                )
            aggregated = self._velocity
        
        # 计算统计信息
        gradient_norms = np.array([u.gradient_norm for u in valid_updates])
        
        elapsed = time.time() - start_time
        self.total_aggregations += 1
        
        return AggregationResult(
            aggregated_update=aggregated,
            strategy="FedAvg",
            num_clients=len(valid_updates),
            total_samples=sum(u.sample_size for u in valid_updates),
            elapsed_time=elapsed,
            metadata={
                "momentum": self.momentum,
                "server_momentum": self.server_momentum,
                "weights": weights.tolist(),
            },
            avg_gradient_norm=float(np.mean(gradient_norms)),
            max_gradient_norm=float(np.max(gradient_norms)),
            min_gradient_norm=float(np.min(gradient_norms)),
            std_gradient_norm=float(np.std(gradient_norms)),
        )


class FedProxAggregator(BaseAggregator):
    """
    FedProx 聚合器
    
    论文: "Federated Optimization in Heterogeneous Networks" (Li et al., 2020)
    
    添加了 proximal term 来处理系统异构性:
        min w Σᵢ (nᵢ/n) · Fᵢ(w) + (μ/2) ||w - w_global||²
    """
    
    def __init__(
        self,
        mu: float = 0.01,  # proximal term 系数
        **kwargs
    ):
        super().__init__(**kwargs)
        self.mu = mu
    
    def aggregate(
        self,
        updates: List[ClientUpdate],
        current_model: Optional[np.ndarray] = None,
        **kwargs
    ) -> AggregationResult:
        """执行 FedProx 聚合"""
        import time
        start_time = time.time()
        
        if current_model is None:
            raise ValueError("FedProx requires current_model")
        
        # 验证和过滤
        valid_updates = [
            u for u in updates
            if not self.validate_updates or self.validate_update(u)
        ]
        
        if len(valid_updates) < self.min_clients:
            raise ValueError(f"Not enough valid updates: {len(valid_updates)}")
        
        # 计算权重
        weights = self.compute_weights(valid_updates)
        
        # 加权平均
        aggregated = np.zeros_like(valid_updates[0].model_update)
        for update, w in zip(valid_updates, weights):
            aggregated += w * update.model_update
        
        # 添加 proximal correction
        # FedProx 的更新规则: w = w - η * (Δw + μ * (w - w_global))
        # 这里我们只返回 Δw，实际更新在外部处理
        proximal_term = self.mu * (np.mean(valid_updates[0].model_update) - 
                                    np.mean(current_model))
        aggregated += proximal_term * np.ones_like(aggregated)
        
        elapsed = time.time() - start_time
        
        return AggregationResult(
            aggregated_update=aggregated,
            strategy="FedProx",
            num_clients=len(valid_updates),
            total_samples=sum(u.sample_size for u in valid_updates),
            elapsed_time=elapsed,
            metadata={
                "mu": self.mu,
                "proximal_correction": proximal_term,
            },
        )


class KrumAggregator(BaseAggregator):
    """
    Krum 聚合器 - 拜占庭容错聚合
    
    论文: "Machine Learning with Adversaries: Byzantine Tolerant Gradient 
           Descent" (Blanchard et al., 2017)
    
    选择最接近其他更新的更新向量
    """
    
    def __init__(self, f: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.f = f  # 假设的拜占庭客户端数量
    
    def _compute_distances(self, updates: np.ndarray) -> np.ndarray:
        """计算更新之间的距离矩阵"""
        n = len(updates)
        distances = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(updates[i] - updates[j])
                distances[i, j] = dist
                distances[j, i] = dist
        
        return distances
    
    def _krum_score(self, distances: np.ndarray, i: int, f: int) -> float:
        """计算第 i 个更新的 Krum 分数"""
        n = len(distances)
        # 排除自己和 f 个最远的
        sorted_indices = np.argsort(distances[i])
        # 排除自己 (索引0) 和 f 个最远的
        neighbors = sorted_indices[1:n-f]
        return np.sum(distances[i, neighbors])
    
    def aggregate(
        self,
        updates: List[ClientUpdate],
        current_model: Optional[np.ndarray] = None,
        **kwargs
    ) -> AggregationResult:
        """执行 Krum 聚合"""
        import time
        start_time = time.time()
        
        valid_updates = [
            u for u in updates
            if not self.validate_updates or self.validate_update(u)
        ]
        
        n = len(valid_updates)
        if n < 2 * self.f + 2:
            # 如果客户端太少，回退到 FedAvg
            logger.warning("Too few clients for Krum, falling back to FedAvg")
            aggregator = FedAvgAggregator()
            return aggregator.aggregate(updates, current_model)
        
        # 堆叠更新
        update_matrix = np.array([u.model_update for u in valid_updates])
        
        # 计算距离
        distances = self._compute_distances(update_matrix)
        
        # 计算每个更新的分数
        scores = np.array([
            self._krum_score(distances, i, self.f)
            for i in range(n)
        ])
        
        # 选择分数最小的 (或选择 top-k 并平均)
        # 这里使用加权平均: 选择分数最小的 f+1 个
        k = n - self.f
        top_k_indices = np.argsort(scores)[:k]
        
        weights = np.zeros(n)
        weights[top_k_indices] = 1.0 / k
        
        aggregated = np.sum(update_matrix * weights[:, np.newaxis], axis=0)
        
        elapsed = time.time() - start_time
        
        return AggregationResult(
            aggregated_update=aggregated,
            strategy="Krum",
            num_clients=len(valid_updates),
            total_samples=sum(u.sample_size for u in valid_updates),
            elapsed_time=elapsed,
            metadata={
                "f": self.f,
                "krum_scores": scores.tolist(),
                "selected_indices": top_k_indices.tolist(),
            },
            outlier_scores=scores,
        )


class TrimmedMeanAggregator(BaseAggregator):
    """
    Trimmed Mean 聚合器
    
    论文: "Byzantine-Robust Distributed Learning: Towards Optimal Statistical 
           Rates" (Li et al., 2019)
    
    对每个参数位置，去除最大值和最小值后求平均
    """
    
    def __init__(self, beta: float = 0.1, **kwargs):
        """
        Args:
            beta: 剪裁比例，例如 beta=0.1 意味着去除前后的 10%
        """
        super().__init__(**kwargs)
        self.beta = beta
    
    def aggregate(
        self,
        updates: List[ClientUpdate],
        current_model: Optional[np.ndarray] = None,
        **kwargs
    ) -> AggregationResult:
        """执行 Trimmed Mean 聚合"""
        import time
        start_time = time.time()
        
        valid_updates = [
            u for u in updates
            if not self.validate_updates or self.validate_update(u)
        ]
        
        n = len(valid_updates)
        c = int(np.ceil(n * self.beta))  # 要剪裁的数量
        
        if n < 2 * c + 1:
            # 需要至少 2c+1 个客户端
            logger.warning("Too few clients for Trimmed Mean, falling back to FedAvg")
            aggregator = FedAvgAggregator()
            return aggregator.aggregate(updates, current_model)

