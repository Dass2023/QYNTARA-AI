import os
import logging
import uuid
import time

logger = logging.getLogger(__name__)

# Try to import kubernetes library
try:
    from kubernetes import client, config
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False

class KubernetesConnector:
    """
    Unified Interface for Cloud Grid Operations.
    Automatically selects backend:
    1. Real Kubernetes (if library available + config found)
    2. Mock Grid (Fallback)
    """
    
    def __init__(self, namespace="qyntara-gpu-grid"):
        self.namespace = namespace
        self.backend = "MOCK"
        self.api_instance = None
        
        # 1. Try Loading K8s Config
        if K8S_AVAILABLE:
            try:
                # Try in-cluster first, then local kubeconfig
                try:
                    config.load_incluster_config()
                    logger.info("Loaded in-cluster K8s config.")
                except:
                    config.load_kube_config()
                    logger.info("Loaded local kubeconfig.")
                
                self.api_instance = client.CoreV1Api()
                self.backend = "KUBERNETES"
                logger.info(f"Connected to Kubernetes Cluster. Namespace: {namespace}")
                
            except Exception as e:
                logger.warning(f"K8s Config Load Failed (Using Mock): {e}")
        
        # 2. Mock Fallback
        if self.backend == "MOCK":
            logger.warning("No Kubernetes Access. Using Local Grid Mock.")
            self.mock_pods = {}

    def create_gpu_pod(self, job_id, image="qyntara/lrm-v2:latest", gpu_type="nvidia-a100"):
        """
        Deploys a Pod for a GPU job.
        """
        pod_name = f"worker-{job_id}"
        
        if self.backend == "KUBERNETES":
            try:
                # Define Pod Spec
                pod_manifest = {
                    "apiVersion": "v1",
                    "kind": "Pod",
                    "metadata": {"name": pod_name, "labels": {"app": "qyntara-worker"}},
                    "spec": {
                        "containers": [{
                            "name": "gpu-worker",
                            "image": image,
                            "resources": {
                                "limits": {"nvidia.com/gpu": 1} # Request 1 GPU
                            },
                            "env": [{"name": "JOB_ID", "value": job_id}]
                        }],
                        "restartPolicy": "Never"
                    }
                }
                
                resp = self.api_instance.create_namespaced_pod(body=pod_manifest, namespace=self.namespace)
                logger.info(f"K8s Pod Created: {pod_name}")
                return {
                    "pod_id": pod_name,
                    "status": "PENDING",
                    "ip": None # Available later
                }
                
            except Exception as e:
                logger.error(f"K8s Deployment Failed: {e}")
                return None

        else: # MOCK
            self.mock_pods[pod_name] = {"status": "RUNNING", "image": image, "start_time": time.time()}
            logger.info(f"[MOCK] Deployed Pod: {pod_name} (Image: {image})")
            return {
                "pod_id": pod_name,
                "status": "RUNNING",
                "ip": "127.0.0.1"
            }

    def get_pod_status(self, pod_id):
        """
        Checks Pod status.
        """
        if self.backend == "KUBERNETES":
            try:
                resp = self.api_instance.read_namespaced_pod(name=pod_id, namespace=self.namespace)
                return {
                    "pod_id": pod_id,
                    "status": resp.status.phase,
                    "ip": resp.status.pod_ip
                }
            except Exception as e:
                logger.error(f"K8s Status Check Failed: {e}")
                return {"pod_id": pod_id, "status": "UNKNOWN"}
        
        else: # MOCK
            if pod_id in self.mock_pods:
                return {"pod_id": pod_id, "status": "RUNNING", "ip": "127.0.0.1"}
            return {"pod_id": pod_id, "status": "TERMINATED"}

    def delete_pod(self, pod_id):
        """
        Terminates the Pod.
        """
        if self.backend == "KUBERNETES":
            try:
                self.api_instance.delete_namespaced_pod(name=pod_id, namespace=self.namespace)
                logger.info(f"K8s Pod Deleted: {pod_id}")
                return True
            except Exception as e:
                logger.error(f"K8s Delete Failed: {e}")
                return False
        
        else: # MOCK
            if pod_id in self.mock_pods:
                del self.mock_pods[pod_id]
                logger.info(f"[MOCK] Pod Terminated: {pod_id}")
                return True
            return False
