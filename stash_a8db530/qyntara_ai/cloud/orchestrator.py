import logging
import time
from .k8s_client import KubernetesConnector

logger = logging.getLogger(__name__)

class CloudOrchestrator:
    """
    Qyntara Cloud Grid (The Grid).
    
    Responsible for:
    - Microservice Orchestration via K8s Connector.
    - Resource Allocation (GPU/CPU).
    - Job Scheduling.
    
    Current Implementation: v2.0-Beta (Connector Integrated)
    """
    
    def __init__(self, namespace="qyntara-gpu-grid"):
        self.connector = KubernetesConnector(namespace=namespace)
        self.health_status = "HEALTHY"
        logger.info(f"Cloud Orchestrator initialized. Backend: {self.connector.backend}")

    def request_gpu_instance(self, job_id, image="lrm-v2-large"):
        """
        Requests a GPU pod from the Grid.
        """
        result = self.connector.create_gpu_pod(job_id, image=image)
        if result:
            logger.info(f"Grid Response: {result}")
            return result
        return {"status": "FAILED", "error": "Scheduling Error"}

    def release_instance(self, pod_id):
        return self.connector.delete_pod(pod_id)

    def get_cluster_stats(self):
        backend = self.connector.backend
        return {
            "status": self.health_status,
            "backend": backend,
            "nodes_active": "AUTOSCALED" if backend == "KUBERNETES" else 1,
            "active_pods": len(self.connector.mock_pods) if backend == "MOCK" else 1 if backend == "KUBERNETES" else 0,
            "gpu_utilization": "DYNAMIC" if backend == "KUBERNETES" else "Mocked (0%)"
        }
