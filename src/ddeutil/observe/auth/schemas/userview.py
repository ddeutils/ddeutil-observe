# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from .user import UserSchema


class UserView(UserSchema):

    def gen_row(self) -> str:
        """Return a html row value that already map this model attributes.

        :rtype: str
        """
        return (
            f"<td>{self.id}</td>"
            f"<td>{self.username}</td>"
            f"<td>{self.email}</td>"
            f"<td>{self.fullname}</td>"
            f"<td>{self.is_verified}</td>"
        )
