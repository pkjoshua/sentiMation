#!/usr/bin/env python3
"""
Host Scheduler Client for communicating with the Windows host service
"""
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class JobStep:
    """Represents a single step in a job"""
    def __init__(self, name: str, docker_args: Optional[str] = None, timeout_sec: int = 3600, retries: int = 0, step_type: str = 'docker', http: Optional[Dict[str, Any]] = None):
        self.name = name
        self.docker_args = docker_args
        self.timeout_sec = timeout_sec
        self.retries = retries
        self.step_type = step_type  # 'docker' or 'http'
        self.http = http or {}
    
    def to_dict(self) -> Dict[str, Any]:
        base = {
            'name': self.name,
            'timeoutSec': self.timeout_sec,
            'retries': self.retries
        }
        if self.step_type == 'docker':
            base['dockerArgs'] = self.docker_args or ''
        elif self.step_type == 'http':
            base['type'] = 'http'
            base['http'] = self.http
        else:
            raise ValueError(f"Unknown step type: {self.step_type}")
        return base

class JobSpec:
    """Represents a job specification for the host service"""
    def __init__(self, task_name: str, steps: List[JobStep], env: Optional[Dict[str, str]] = None, time: Optional[str] = None, days: Optional[List[str]] = None):
        self.task_name = task_name
        self.steps = steps
        self.env = env or {}
        self.time = time  # HH:mm format for scheduled jobs
        self.days = days or []  # weekly days, e.g., ['Monday','Wednesday']
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'TaskName': self.task_name,
            'Steps': [step.to_dict() for step in self.steps],
            'Env': self.env
        }
        if self.time:
            result['Time'] = self.time
        if self.days:
            result['Days'] = self.days
        return result

class HostSchedulerClient:
    """Client for communicating with the Windows host service"""
    
    def __init__(self, base_url: str = "http://host.docker.internal:7070"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30  # 30 second timeout
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the host service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Making request to {url}")
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Host service response: {result}")
            return result
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Failed to connect to host service at {url}. Is the host service running?"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
            
        except requests.exceptions.Timeout:
            error_msg = f"Request to host service timed out after 30 seconds"
            logger.error(error_msg)
            raise TimeoutError(error_msg)
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Host service returned HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse response from host service: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error communicating with host service: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def schedule_job(self, job: JobSpec) -> Dict[str, Any]:
        if not job.time:
            raise ValueError("Job must have a time specified for scheduling")
        data = job.to_dict()
        logger.info(f"Scheduling job: {job.task_name} at {job.time}")
        result = self._make_request("/schedule", data)
        if result.get('status') != 'ok':
            raise RuntimeError(f"Host service failed to schedule job: {result}")
        return result
    
    def run_job_now(self, job: JobSpec) -> Dict[str, Any]:
        data = job.to_dict()
        logger.info(f"Running job immediately: {job.task_name}")
        result = self._make_request("/run-now", data)
        if result.get('status') != 'ok':
            raise RuntimeError(f"Host service failed to run job: {result}")
        return result
    
    def is_available(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def delete_task(self, task_name: str) -> Dict[str, Any]:
        data = { 'TaskName': task_name }
        logger.info(f"Deleting task in host scheduler: {task_name}")
        result = self._make_request("/delete", data)
        if result.get('status') != 'ok':
            raise RuntimeError(f"Host service failed to delete task: {result}")
        return result

# Helpers to build HTTP callback steps

def build_http_callback_step(name: str, url: str, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout_sec: int = 3600, retries: int = 0) -> JobStep:
    return JobStep(
        name=name,
        step_type='http',
        timeout_sec=timeout_sec,
        retries=retries,
        http={
            'method': 'POST',
            'url': url,
            'headers': headers or {},
            'body': json.dumps(body),
            'contentType': 'application/json'
        }
    )

# Factory function now builds callback steps instead of docker runs
import os

def create_generator_job_steps(generator_type: str, prompt: str = None, character: str = None, environment: str = None,
                               webapp_public_url: str = 'http://localhost:5000', host_callback_token: str = 'dev',
                               job_id: Optional[int] = None, task_name: Optional[str] = None) -> List[JobStep]:
    steps: List[JobStep] = []
    callback_url = f"{webapp_public_url}/api/host/run-job"
    body = {
        'type': generator_type,
        'prompt': prompt,
        'character': character,
        'environment': environment,
    }
    if job_id is not None:
        body['jobId'] = job_id
    if task_name is not None:
        body['taskName'] = task_name
    headers = {
        'Authorization': f"Bearer {host_callback_token}"
    }
    steps.append(build_http_callback_step("invoke_webapp_runner", callback_url, body, headers=headers, timeout_sec=7200, retries=0))
    return steps
