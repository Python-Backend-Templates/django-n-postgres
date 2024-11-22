from typing import TYPE_CHECKING, Dict, List, TypeAlias

from rest_framework.throttling import BaseThrottle
from rest_framework.viewsets import GenericViewSet

ActionToScope: TypeAlias = Dict[str, str]


if TYPE_CHECKING:
    _Base = GenericViewSet
else:
    _Base = object


class ThrottlingScopePerActionMixin(_Base):  # type:ignore[valid-type,misc]
    action_to_throttle_scope: ActionToScope = dict()

    def get_throttles(self) -> List[BaseThrottle]:
        for action, scope in self.action_to_throttle_scope.items():
            if self.action == action:
                self.throttle_scope = scope
                break
        return super().get_throttles()
