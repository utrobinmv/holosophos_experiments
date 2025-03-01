import os
import time
import base64
import traceback

from dotenv import load_dotenv

from vastai_sdk import VastAI


BASE_IMAGE = "nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04"
DEFAULT_GPU_TYPE = "RTX_3090"


def wait_for_instance(
    vast_sdk: VastAI, instance_id: str, max_wait_time: int = 600
) -> bool:
    print(f"Waiting for instance {instance_id} to be ready...")
    start_wait = time.time()
    instance_ready = False
    while time.time() - start_wait < max_wait_time:
        instance_details = vast_sdk.show_instance(id=instance_id)
        if (
            isinstance(instance_details, dict)
            and instance_details.get("actual_status") == "running"
        ):
            instance_ready = True
            print(f"Instance {instance_id} is running and ready.")
            break
        print(f"Instance {instance_id} not ready yet. Waiting...")
        time.sleep(15)
    return instance_ready


def select_instance(vast_sdk: VastAI, gpu_name: str) -> int:
    params = [
        f"gpu_name={gpu_name}",
        "cuda_vers>=12.1",
        "num_gpus=1",
        "reliability > 0.99",
        "inet_up > 400",
        "inet_down > 400",
        "verified=True",
        "rentable=True",
        "disk_space > 100",
    ]
    query = "  ".join(params)
    order = "score-"
    offers = vast_sdk.search_offers(query=query, order=order)
    assert offers
    return int(offers[0]["id"])


def gpu_job(code: str, gpu_type: str = DEFAULT_GPU_TYPE, max_runtime: int = 600):
    load_dotenv()
    instance_id = None
    sdk = VastAI(api_key=os.getenv("VAST_AI_KEY"))
    try:
        print(f"Selecting instance with {gpu_type}...")
        offer_id = select_instance(sdk, gpu_type)

        code_b64 = base64.b64encode(code.encode()).decode()
        onstart_cmd = (
            f'python3 -c "import base64; '
            f"open('/root/script.py', 'wb').write(base64.b64decode('{code_b64}')); "
            f"print('Running user code...'); "
            f"import subprocess; "
            f"result = subprocess.run(['python3', '/root/script.py'], capture_output=True, text=True); "
            f"logs = result.stdout + '\\n' + result.stderr; "
            f"open('/root/output.log', 'w').write(logs); "
            f"print('Execution finished. Logs:', logs)\""
        )

        print(f"Launching offer {offer_id}...")
        instance = sdk.create_instance(
            id=offer_id,
            image=BASE_IMAGE,
            disk=50.0,
            onstart_cmd=onstart_cmd,
        )
        assert instance["success"], "Create intance was not successful"
        instance_id = instance["new_contract"]
        print(f"Instance launched successfully. ID: {instance_id}")

        is_ready = wait_for_instance(sdk, instance_id)
        if not is_ready:
            print(f"Instance {instance_id} is not ready in time, destroying...")
            sdk.destroy_instance(id=instance_id)
            return

        start_time = time.time()
        while time.time() - start_time < max_runtime:
            sdk.execute(id=instance_id, COMMAND="ls /root")
            ls_result = sdk.last_output
            print("ls result:", ls_result.replace("\n", " "))
            if ls_result and "output.log" in ls_result:
                sdk.logs(INSTANCE_ID=instance_id)
                logs = sdk.last_output
                print("Execution completed, retrieved logs:")
                print(logs)
                break

            time.sleep(5)

        print("Cleaning up...")
        sdk.destroy_instance(id=instance_id)
    except Exception:
        print(traceback.format_exc())
        if instance_id is not None:
            print(f"Destroying instance {instance_id}...")
            sdk.destroy_instance(id=instance_id)
            return


if __name__ == "__main__":
    gpu_job("print('Hello world!')")
