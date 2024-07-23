import uuid
import weakref
from inspect import signature
from typing import Union, Callable, List, Dict, Iterable, Optional, Any, Tuple

from aidial_sdk.chat_completion.actions import ActionArgumentSchema, Action
from aidial_sdk.utils.logging import log_debug, log_error


class ActionRegistry:
    def __init__(self):
        self._actions = weakref.WeakValueDictionary()
        self._registered_actions: Dict[str, Action] = {}

    def register(self, action: Callable) -> str:
        action_id = str(uuid.uuid4())
        self._actions[action_id] = action
        return action_id

    def has(self, action_id: str) -> bool:
        return action_id in self._actions

    def call(self, action_id: str, *args, **kwargs) -> Optional[Any]:
        action = self._actions.get(action_id)
        if action:
            return action(*args, **kwargs)
        else:
            self._handle_error_no_action_found(action_id)

    def delete(self, action_id: str):
        if action_id in self._actions:
            del self._actions[action_id]
        else:
            self._handle_error_no_action_found(action_id)

    def clear(self):
        self._actions.clear()
        self._registered_actions.clear()

    def _generate_argument_schemas(self, func: Callable) -> Tuple[Dict[str, ActionArgumentSchema], List[str]]:
        sig = signature(func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            arg_type = "string" if param.annotation is param.empty else param.annotation.__name__
            parameter_schema = ActionArgumentSchema(
                type=arg_type,
                description=f"Argument {param_name}",
                default=param.default if param.default is not param.empty else None
            )

            if param.default is param.empty:
                required.append(param_name)

            properties[param_name] = parameter_schema

        return properties, required

    def set_actions(self, action_definitions: List[Dict[str, Any]]) -> List[Action]:
        self.clear()
        return self.add_actions(action_definitions)

    def add_actions(self, action_definitions: List[Dict[str, Any]]) -> List[Action]:
        added_actions = []

        for definition in action_definitions:
            func = definition["function"]
            action_id = self.register(func)

            parameters, required = self._generate_argument_schemas(func)

            action_details = {
                "name": definition["name"],
                "label": definition.get("label", definition["name"]),
                "action_id": action_id,
                "description": definition.get("description"),
                "parameters": parameters,
                "required": required
            }

            action = Action(**action_details)
            self._registered_actions[action_id] = action
            added_actions.append(action)

        return added_actions

    def remove_actions(self, action_ids: List[str]) -> List[Action]:
        for action_id in action_ids:
            if action_id in self._registered_actions:
                del self._registered_actions[action_id]
                self.delete(action_id)
            else:
                self._handle_error_no_action_found(action_id)

        return self.get_actions()

    def get_actions(self) -> List[Action]:
        return list(self._registered_actions.values())

    def call_action(self, action_id: str, *args, **kwargs) -> Optional[Any]:
        if self.has(action_id):
            return self.call(action_id, *args, **kwargs)
        else:
            self._handle_error_no_action_found(action_id)

    def _handle_error_no_action_found(self, action_id: str, strict: bool = False) -> None:
        error = f"No action registered with id: {action_id}"
        if strict:
            log_error(error)
            raise KeyError(error)
        else:
            log_debug(error)