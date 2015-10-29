# Copyright 2015 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Welcome

Welcome provides user with language selection

"""
import logging
from urwid import (Pile, Columns, Text, ListBox)
from subiquity.ui.buttons import done_btn, cancel_btn
from subiquity.ui.interactive import (PasswordEditor,
                                      StringEditor,
                                      UsernameEditor)
from subiquity.ui.utils import Padding, Color
from subiquity.view import ViewPolicy

log = logging.getLogger("subiquity.views.identity")


class IdentityView(ViewPolicy):
    def __init__(self, model, signal):
        self.model = model
        self.signal = signal
        self.items = []
        self.realname = StringEditor(caption="")
        self.username = UsernameEditor(caption="")
        self.password = PasswordEditor(caption="")
        self.error = Text("", align="center")
        self.confirm_password = PasswordEditor(caption="")

        body = [
            Padding.center_50(self._build_model_inputs()),
            Padding.line_break(""),
            Padding.center_50(Color.info_error(self.error)),
            Padding.line_break(""),
            Padding.center_15(self._build_buttons()),
        ]
        super().__init__(ListBox(body))

    def _build_buttons(self):
        cancel = cancel_btn(on_press=self.cancel)
        done = done_btn(on_press=self.done)

        buttons = [
            Color.button(done, focus_map='button focus'),
            Color.button(cancel, focus_map='button focus')
        ]
        return Pile(buttons)

    def _build_model_inputs(self):
        sl = [
            Columns(
                [
                    ("weight", 0.2, Text("Real Name", align="right")),
                    ("weight", 0.3,
                     Color.string_input(self.realname,
                                        focus_map="string_input focus"))
                ],
                dividechars=4
            ),
            Columns(
                [
                    ("weight", 0.2, Text("Username", align="right")),
                    ("weight", 0.3,
                     Color.string_input(self.username,
                                        focus_map="string_input focus"))
                ],
                dividechars=4
            ),
            Columns(
                [
                    ("weight", 0.2, Text("Password", align="right")),
                    ("weight", 0.3,
                     Color.string_input(self.password,
                                        focus_map="string_input focus"))
                ],
                dividechars=4
            ),
            Columns(
                [
                    ("weight", 0.2, Text("Confirm Password", align="right")),
                    ("weight", 0.3,
                     Color.string_input(self.confirm_password,
                                        focus_map="string_input focus"))
                ],
                dividechars=4
            )
        ]
        return Pile(sl)

    def done(self, result):
        if self.password.value != self.confirm_password.value:
            self.error.set_text("Passwords do not match.")
            self.password.value = ""
            self.confirm_password.value = ""
            return

        if len(self.username.value) > 32:
            self.error.set_text("Username too long, must be < 32")
            self.username.value = ""
            return

        cpassword = self.model.encrypt_password(self.password.value)
        log.debug("*crypted* User input: {} {} {}".format(
            self.username.value, cpassword, cpassword))
        result = {
            "realname": self.realname.value,
            "username": self.username.value,
            "password": cpassword,
            "confirm_password": cpassword,
        }

        log.debug("User input: {}".format(result))
        self.signal.emit_signal('installprogress:curtin-install', result)

    def cancel(self, button):
        self.signal.prev_signal()
