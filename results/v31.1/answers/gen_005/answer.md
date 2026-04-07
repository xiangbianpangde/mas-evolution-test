# gen_005 Answer

**Run**: 1
**Iterations**: 1

## Answer

# 去中心化身份认证（DID）系统实现

## 📐 架构简图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        去中心化身份认证 (DID) 系统架构                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   Holder    │     │    Issuer   │     │  Verifier   │                   │
│  │  (持有者)   │     │  (签发者)   │     │ (验证者)    │                   │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                   │
│         │                   │                   │                          │
│         │   1. 创建DID      │   2. 发行VC        │   3. 验证VC              │
│         ▼                   ▼                   ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                      DID Client SDK                          │          │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │          │
│  │  │ DID Creation │  │ VC Signing   │  │ VC Verify    │       │          │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                    │                                       │
│                                    ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    DID Registry (区块链)                     │          │
│  │  ┌─────────────────────────────────────────────────────┐   │          │
│  │  │  did:example:1234567890abcdef1234567890abcdef       │   │          │
│  │  │  {                                                     │   │          │
│  │  │    "@context": "https://www.w3.org/ns/did/v1",        │   │          │
│  │  │    "id": "did:example:1234...",                       │   │          │
│  │  │    "verificationMethod": [...],                       │   │          │
│  │  │    "authentication": [...],                           │   │          │
│  │  │    "serviceEndpoint": [...]                           │   │          │
│  │  │  }                                                     │   │          │
│  │  └─────────────────────────────────────────────────────┘   │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    加密原语层                                 │          │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐            │          │
│  │  │Ed25519 │  │ secp256│  │  BLS   │  │  RSA   │            │          │
│  │  │ 签名   │  │k1 签名 │  │ 签名   │  │ 签名   │            │          │
│  │  └────────┘  └────────┘  └────────┘  └────────┘            │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            数据流时序图                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Holder              Issuer              Registry           Verifier        │
│    │                   │                    │                  │            │
│    │─[1] Generate DID─>│                    │                  │            │
│    │                   │                    │                  │            │
│    │   [2] Register DID to Blockchain]       │                  │            │
│    │<────────────────────────────────────────│                  │            │
│    │                   │                    │                  │            │
│    │─[3] Request VC ──>│                    │                  │            │
│    │                   │                    │                  │            │
│    │                   │─[4] Issue VC ───────>│                  │            │
│    │<[5] Receive VC]───│                    │                  │            │
│    │                   │                    │                  │            │
│    │─[6] Present VP ──────────────────────────────────────────>│            │
│    │                   │                    │                  │            │
│    │                   │                    │<─[7] Verify VP ──│            │
│    │                   │                    │                  │            │
│    │<─[8] Result]──────────────────────────────────────────────│            │
│    │                   │                    │                  │            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 核心代码（完整可运行）

```python
#!/usr/bin/env python3
"""
去中心化身份认证 (DID) 系统实现
Decentralized Identifier (DID) System Implementation

基于 W3C DID Core Specification
参考: https://www.w3.org/TR/did-core/

作者: 技术分析师
版本: 1.0.0
"""

import hashlib
import json
import time
import uuid
import base64
import hmac
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import copy


# ============================================================================
# 第一部分：密码学基础
# ============================================================================

class KeyType(Enum):
    """支持的密钥类型"""
    Ed25519 = "Ed25519"
    Ed448 = "Ed448"
    secp256k1 = "secp256k1"
    RSA = "RSA2048"
    BLS12381G1 = "BLS12381G1"
    BLS12381G2 = "BLS12381G2"


class KeyAgreementAlgorithm(Enum):
    """密钥协商算法"""
    ECDH = "ECDH"
    DH = "DH"
    X25519 = "X25519"


@dataclass
class PublicKey:
    """公钥数据结构"""
    id: str
    type: KeyType
    controller: str
    public_key_hex: str
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "controller": self.controller,
            "publicKeyHex": self.public_key_hex
        }


@dataclass
class PrivateKey:
    """私钥数据结构（内存中持有，不持久化存储）"""
    id: str
    type: KeyType
    private_key_hex: str
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            # 注意：实际应用中永远不要返回私钥
            "privateKeyHex": "***REDACTED***"
        }


class CryptoService:
    """密码学服务层 - 实现签名和验证"""
    
    # 模拟密钥对生成
    @staticmethod
    def generate_key_pair(key_type: KeyType) -> Tuple[PublicKey, PrivateKey]:
        """生成密钥对"""
        key_id = f"{uuid.uuid4().hex[:16]}"
        
        # 模拟生成密钥（实际使用 cryptography 库）
        if key_type == KeyType.Ed25519:
            # Ed25519 密钥是 32 字节
            private_bytes = hashlib.sha256(f"{key_id}_private".encode()).digest()
            public_bytes = hashlib.sha256(f"{key_id}_public".encode()).digest()
        elif key_type == KeyType.secp256k1:
            # secp256k1 密钥是 32 字节
            private_bytes = hashlib.sha256(f"{key_id}_private_secp".encode()).digest()
            public_bytes = hashlib.sha256(f"{key_id}_public_secp".encode()).digest()
        else:
            # 默认使用 SHA-256 生成模拟密钥
            private_bytes = hashlib.sha256(f"{key_id}_private".encode()).digest()
            public_bytes = hashlib.sha256(f"{key_id}_public".encode()).digest()
        
        private_key = PrivateKey(
            id=key_id,
            type=key_type,
            private_key_hex=private_bytes.hex()
        )
        
        public_key = PublicKey(
            id=key_id,
            type=key_type,
            controller="",  # 稍后设置
            public_key_hex=public_bytes.hex()
        )
        
        return public_key, private_key
    
    @staticmethod
    def sign(data: str, private_key: PrivateKey) -> str:
        """对数据进行签名"""
        message = data.encode('utf-8')
        key = private_key.private_key_hex.encode('utf-8')
        
        # 使用 HMAC-SHA256 模拟签名
        signature = hmac.new(key, message, hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def verify(data: str, signature: str, public_key: PublicKey) -> bool:
        """验证签名"""
        try:
            message = data.encode('utf-8')
            key = public_key.public_key_hex.encode('utf-8')
            
            expected_signature = hmac.new(key, message, hashlib.sha256).digest()
            actual_signature = base64.b64decode(signature.encode('utf-8'))
            
            return hmac.compare_digest(expected_signature, actual_signature)
        except Exception:
            return False
    
    @staticmethod
    def hash(data: str) -> str:
        """计算数据哈希"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()


# ============================================================================
# 第二部分：DID 核心实现
# ============================================================================

class DIDMethod(Enum):
    """DID 方法枚举"""
    EXAMPLE = "example"
    WEB = "web"
    ETHR = "ethr"
    ION = "ion"
    KEY = "key"
    ISO_18013 = "iso18013"


@dataclass
class ServiceEndpoint:
    """服务端点"""
    id: str
    type: str
    service_endpoint: str
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "serviceEndpoint": self.service_endpoint
        }


@dataclass
class DIDDocument:
    """DID Document - W3C 标准格式"""
    context: List[str] = field(default_factory=lambda: [
        "https://www.w3.org/ns/did/v1",
        "https://w3id.org/security/v1"
    ])
    id: str = ""
    also_known_as: List[str] = field(default_factory=list)
    controller: List[str] = field(default_factory=list)
    verification_method: List[Dict] = field(default_factory=list)
    authentication: List[str] = field(default_factory=list)
    assertion_method: List[str] = field(default_factory=list)
    key_agreement: List[str] = field(default_factory=list)
    capability_invocation: List[str] = field(default_factory=list)
    capability_delegation: List[str] = field(default_factory=list)
    service: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为标准 JSON-LD 格式"""
        doc = {
            "@context": self.context,
            "id": self.id,
        }
        
        if self.also_known_as:
            doc["alsoKnownAs"] = self.also_known_as
        if self.controller:
            doc["controller"] = self.controller
        if self.verification_method:
            doc["verificationMethod"] = self.verification_method
        if self.authentication:
            doc["authentication"] = self.authentication
        if self.assertion_method:
            doc["assertionMethod"] = self.assertion_method
        if self.key_agreement:
            doc["keyAgreement"] = self.key_agreement
        if self.capability_invocation:
            doc["capabilityInvocation"] = self.capability_invocation
        if self.capability_delegation:
            doc["capabilityDelegation"] = self.capability_delegation
        if self.service:
            doc["service"] = self.service
            
        return doc
    
    @staticmethod
    def from_dict(data: Dict) -> 'DIDDocument':
        """从字典创建 DID Document"""
        doc = DIDDocument()
        doc.id = data.get("id", "")
        
        if "@context" in data:
            if isinstance(data["@context"], list):
                doc.context = data["@context"]
            else:
                doc.context = [data["@context"]]
                
        doc.also_known_as = data.get("alsoKnownAs", [])
        doc.controller = data.get("controller", [])
        doc.verification_method = data.get("verificationMethod", [])
        doc.authentication = data.get("authentication", [])
        doc.assertion_method = data.get("assertionMethod", [])
        doc.key_agreement = data.get("keyAgreement", [])
        doc.capability_invocation = data.get("capabilityInvocation", [])
        doc.capability_delegation = data.get("capabilityDelegation", [])
        doc.service = data.get("service", [])
        
        return doc


class DID:
    """DID 标识符处理"""
    
    # 标准格式: did:method:namespace-specific-identifier
    PATTERN = r"^did:([a-z0-9]+):([a-zA-Z0-9._-]+)$"
    
    def __init__(self, method: str, namespace: str, specific_id: str):
        self.method = method
        self.namespace = namespace
        self.specific_id = specific_id
    
    @property
    def uri(self) -> str:
        """返回完整的 DID URI"""
        return f"did:{self.method}:{self.namespace}{self.specific_id}"
    
    @classmethod
    def parse(cls, did_uri: str) -> Optional['DID']:
        """解析 DID URI"""
        parts = did_uri.split(":")
        if len(parts) != 3 or parts[0] != "did":
            return None
        return cls(method=parts[1], namespace="", specific_id=parts[2])
    
    @classmethod
    def create(cls, method: DIDMethod, specific_id: str) -> 'DID':
        """创建新的 DID"""
        return cls(method=method.value, namespace="", specific_id=specific_id)
    
    def __str__(self) -> str:
        return self.uri
    
    def __eq__(self, other) -> bool:
        if isinstance(other, DID):
            return self.uri == other.uri
        return False


# ============================================================================
# 第三部分：去中心化注册表（模拟区块链）
# ============================================================================

@dataclass
class DIDRecord:
    """区块链上的 DID 记录"""
    did: str
    document: Dict
    created: str
    updated: str
    version_id: int
    transaction_hash: str
    block_number: int
    active: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)


class DIDRegistry:
    """DID 注册表 - 模拟区块链存储"""
    
    def __init__(self):
        self.records: Dict[str, DIDRecord] = {}
        self.transaction_log: List[Dict] = []
        self.block_height = 0
    
    def register(self, did: str, document: DIDDocument, 
                 transaction_metadata: Optional[Dict] = None) -> DIDRecord:
        """注册新的 DID"""
        if did in self.records:
            raise ValueError(f"DID {did} 已存在")
        
        self.block_height += 1
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # 生成交易哈希
        tx_data = f"{did}:{json.dumps(document.to_dict())}:{timestamp}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        record = DIDRecord(
            did=did,
            document=document.to_dict(),
            created=timestamp,
            updated=timestamp,
            version_id=1,
            transaction_hash=tx_hash,
            block_number=self.block_height,
            active=True
        )
        
        self.records[did] = record
        self._log_transaction("register", did, tx_hash, document.to_dict())
        
        return record
    
    def update(self, did: str, document: DIDDocument) -> DIDRecord:
        """更新 DID Document"""
        if did not in self.records:
            raise ValueError(f"DID {did} 不存在")
        
        timestamp = datetime.now(timezone.utc).isoformat()
        record = self.records[did]
        
        # 生成新交易哈希
        tx_data = f"{did}:{json.dumps(document.to_dict())}:{timestamp}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        updated_record = DIDRecord(
            did=did,
            document=document.to_dict(),
            created=record.created,
            updated=timestamp,
            version_id=record.version_id + 1,
            transaction_hash=tx_hash,
            block_number=self.block_height,
            active=True
        )
        
        self.records[did] = updated_record
        self._log_transaction("update", did, tx_hash, document.to_dict())
        
        return updated_record
    
    def deactivate(self, did: str) -> bool:
        """停用 DID"""
        if did not in self.records:
            raise ValueError(f"DID {did} 不存在")
        
        self.records[did].active = False
        self._log_transaction("deactivate", did, "", {})
        return True
    
    def resolve(self, did: str) -> Optional[DIDRecord]:
        """解析 DID"""
        return self.records.get(did)
    
    def resolve_document(self, did: str) -> Optional[DIDDocument]:
        """解析 DID Document"""
        record = self.records.get(did)
        if record and record.active:
            return DIDDocument.from_dict(record.document)
        return None
    
    def _log_transaction(self, operation: str, did: str, 
                         tx_hash: str, data: Dict):
        """记录交易日志"""
        self.transaction_log.append({
            "operation": operation,
            "did": did,
            "transaction_hash": tx_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "block_number": self.block_height,
            "data_hash": hashlib.sha256(
                json.dumps(data, sort_keys=True).encode()
            ).hexdigest()
        })


# ============================================================================
# 第四部分：Verifiable Credentials (VC)
# ============================================================================

@dataclass
class CredentialSubject:
    """凭证持有者信息"""
    id: str
    claims: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        result = {"id": self.id}
        result.update(self.claims)
        return result


@dataclass
class CredentialStatus:
    """凭证状态"""
    id: str
    type: str
    revocation_list_bitstring: Optional[str] = None
    
    def to_dict(self) -> Dict:
        result = {"id": self.id, "type": self.type}
        if self.revocation_list_bitstring:
            result["revocationListBitstring"] = self.revocation_list_bitstring
        return result


@dataclass
class VerifiableCredential:
    """可验证凭证 (VC)"""
    context: List[str] = field(default_factory=lambda: [
        "https://www.w3.org/2018/credentials/v1"
    ])
    type: List[str] = field(default_factory=lambda: ["VerifiableCredential"])
    id: str = ""
    issuer: str = ""
    issuance_date: str = ""
    expiration_date: Optional[str] = None
    credential_subject: CredentialSubject = None
    credential_status: Optional[CredentialStatus] = None
    
    # 签名相关
    proof: Optional[Dict] = None
    
    def to_dict(self, include_proof: bool = True) -> Dict:
        """转换为 JSON 格式"""
        result = {
            "@context": self.context,
            "type": self.type,
            "id": self.id,
            "issuer": self.issuer,
            "issuanceDate": self.issuance_date,
            "credentialSubject": self.credential_subject.to_dict()
        }
        
        if self.expiration_date:
            result["expirationDate"] = self.expiration_date
        if self.credential_status:
            result["credentialStatus"] = self.credential_status.to_dict()
        if include_proof and self.proof:
            result["proof"] = self.proof
            
        return result
    
    @staticmethod
    def from_dict(data: Dict) -> 'VerifiableCredential':
        """从字典创建 VC"""
        vc = VerifiableCredential()
        vc.context = data.get("@context", [])
        vc.type = data.get("type", [])
        vc.id = data.get("id", "")
        vc.issuer = data.get("issuer", "")
        vc.issuance_date = data.get("issuanceDate", "")
        vc.expiration_date = data.get("expirationDate")
        
        subject_data = data.get("credentialSubject", {})
        vc.credential_subject = CredentialSubject(
            id=subject_data.get("id", ""),
            claims={k: v for k, v in subject_data.items() if k != "id"}
        )
        
        if "credentialStatus" in data:
            status_data = data["credentialStatus"]
            vc.credential_status = CredentialStatus(
                id=status_data.get("id", ""),
                type=status_data.get("type", ""),
                revocation_list_bitstring=status_data.get("revocationListBitstring")
            )
        
        vc.proof = data.get("proof")
        
        return vc


# ============================================================================
# 第五部分：Verifiable Presentation (VP)
# ============================================================================

@dataclass
class VerifiablePresentation:
    """可验证呈现 (VP)"""
    context: List[str] = field(default_factory=lambda: [
        "https://www.w3.org/2018/credentials/v1",
        "https://www.w3.org/2018/credentials/examples/v1"
    ])
    type: List[str] = field(default_factory=list)
    id: str = ""
    holder: str = ""
    verifiable_credential: List[Dict] = field(default_factory=list)
    
    # 签名相关
    proof: Optional[Dict] = None
    
    def to_dict(self, include_proof: bool = True) -> Dict:
        """转换为 JSON 格式"""
        result = {
            "@context":
