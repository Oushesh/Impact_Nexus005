from pathlib import Path
from typing import Dict, Union
import yaml


def get_flow(config_dict_or_path: Union[Path, Dict], is_file=True):
    flow_config: Dict = {}
    if is_file:
        assert isinstance(
            config_dict_or_path, Path
        ), "If is_file=True, config_file_or_path needs to be Path like"
        assert config_dict_or_path.suffix in [
            ".yaml",
            ".yml",
        ], "Config file needs to be in yaml format"
        with open(config_dict_or_path, "r") as file:  # type: ignore
            flow_config = yaml.safe_load(file)
    else:
        assert isinstance(config_dict_or_path, dict)
        flow_config = config_dict_or_path  # type: ignore

    ## initialize empty flow
    flow = f"Component()"

    ## populate flow with components from the config
    for component in flow_config["Pipeline"]["Components"][::-1]:
        flow = f"{component['name']}({flow}, config={flow_config['Pipeline'].get('Config', {})}, \
            component_config={component.get('component_config', {})}, evaluation_config={component.get('evaluation_config', {})})"
    return flow


def get_config(config_path: Path):
    with open(config_path, "r") as file:
        flow_config = yaml.safe_load(file)
    return flow_config
