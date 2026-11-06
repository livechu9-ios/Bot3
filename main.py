import discord
from discord.ext import commands
import asyncio
import getpass
import hashlib
import io
import os
import re
import struct

TOKEN = os.getenv("MTU2ODE0MzczMTIxODE5MDM1Nw.GpHJ4l.4YyVUQoKhEePsn2QUwEdO9lszfLjZmELSQ7ZSo") or getpass.getpass("Nhap BOT TOKEN moi: ")

FILE_PATTERN = re.compile(r"^assetindexer\.[A-Za-z0-9~]+$")
MAX_SIZE = 20 * 1024 * 1024

KEYWORDS = {
    "scaleHead": ["head", "đầu"],
    "scaleNeck": ["neck", "cổ", "co"],
    "scaleArm": ["arm", "tay", "hand", "shoulder", "elbow",
                 "wrist", "cánh tay", "bàn tay", "vai", "khuỷu"],
    "scaleLeg": ["leg", "chân", "foot", "thigh", "knee",
                 "ankle", "đùi", "đầu gối", "cổ chân", "bàn chân"],
    "flipHead": ["head", "đầu"],
    "flipArm": ["arm", "tay", "hand", "shoulder", "elbow",
                "wrist", "cánh tay", "bàn tay", "vai", "khuỷu"],
    "flipLeg": ["leg", "chân", "foot", "thigh", "knee",
                "ankle", "đùi", "đầu gối", "cổ chân", "bàn chân"]
}

FUNCTIONS = [
    ("scaleFull", "📏 Scale Full"),
    ("scaleHead", "🗿 Scale Head"),
    ("scaleNeck", "🦒 Scale Neck"),
    ("scaleArm", "💪 Scale Arm"),
    ("scaleLeg", "🦵 Scale Leg"),
    ("moveFull", "↕️ Move Full"),
    ("flipHead", "🔄 Flip Head"),
    ("flipArm", "🔄 Flip Arm"),
    ("flipLeg", "🔄 Flip Leg"),
    ("checksum", "🔐 Fix Checksum")
]


def read_float(data, offset):
    try:
        return struct.unpack_from("<f", data, offset)[0]
    except Exception:
        return None


def write_float(data, offset, value):
    struct.pack_into("<f", data, offset, value)


def parse_binary(data):
    bones = []
    seen = set()

    for match in re.finditer(rb"bone_[A-Za-z0-9_~.-]+", data):
        name = match.group().decode("utf-8", errors="ignore")

        if name in seen:
            continue

        seen.add(name)
        start = match.start()
        end = match.end()

        pos_offset = None

        for offset in range(max(0, start - 100), min(len(data) - 12, end + 100)):
            values = [
                read_float(data, offset),
                read_float(data, offset + 4),
                read_float(data, offset + 8)
            ]

            if all(v is not None and -10 <= v <= 10 for v in values):
                pos_offset = offset
                break

        scale_offset = None

        if pos_offset is not None:
            for offset in range(pos_offset + 12, min(len(data) - 12, pos_offset + 40)):
                values = [
                    read_float(data, offset),
                    read_float(data, offset + 4),
                    read_float(data, offset + 8)
                ]

                if all(v is not None and 0.01 <= v <= 100 for v in values):
                    scale_offset = offset
                    break

        bones.append({
            "name": name.lower(),
            "pos": pos_offset,
            "scale": scale_offset
        })

    return bones


def select_bones(bones, function):
    if function in ("scaleFull", "moveFull", "checksum"):
        return bones

    keywords = KEYWORDS.get(function, [])
    return [
        bone for bone in bones
        if any(word in bone["name"] for word in keywords)
    ]


def fix_checksum(data):
    marker = data.find(b"CAB-")

    if marker < 0:
        return data

    start = marker + 4

    if start + 32 > len(data):
        return data

    temp = bytearray(data)
    temp[start:start + 32] = b"0" * 32

    checksum = hashlib.md5(temp).hexdigest().upper().encode("ascii")
    data[start:start + 32] = checksum

    return data


def process_data(original, bones, function, value=None):
    data = bytearray(original)

    if function == "checksum":
        return fix_checksum(data), 1

    targets = select_bones(bones, function)
    changed = 0

    for bone in targets:
        pos = bone["pos"]
        scale = bone["scale"]

        if function.startswith("scale"):
            if scale is None:
                continue

            for i in range(3):
                old = read_float(data, scale + i * 4)
                write_float(data, scale + i * 4, old * value)

            changed += 1

        elif function == "moveFull":
            if pos is None:
                continue

            old = read_float(data, pos + 4)
            write_float(data, pos + 4, old + value)
            changed += 1

        elif function.startswith("flip"):
            if scale is None:
                continue

            old = read_float(data, scale + 4)
            write_float(data, scale + 4, -old)
            changed += 1

    return fix_checksum(data), changed


class ValueModal(discord.ui.Modal):
    def __init__(self, view, function):
        super().__init__(title="VC UMA BONE PRO")
        self.parent_view = view
        self.function = function

        self.number = discord.ui.TextInput(
            label="Nhập giá trị",
            placeholder="Ví dụ: 1.5 hoặc 0.1",
            required=True,
            max_length=12
        )
        self.add_item(self.number)

    async def on_submit(self, interaction):
        try:
            value = float(str(self.number.value))

            if not (-100 <= value <= 100):
                raise ValueError()

            if self.function.startswith("scale") and value <= 0:
                raise ValueError()

            await self.parent_view.run_function(
                interaction, self.function, value
            )

        except ValueError:
            await interaction.response.send_message(
                "❌ Giá trị không hợp lệ!",
                ephemeral=True
            )


class FunctionSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=key)
            for key, name in FUNCTIONS
        ]

        super().__init__(
            placeholder="⚙️ CHỌN CHỨC NĂNG UMA",
            options=options
        )

    async def callback(self, interaction):
        self.view.selected = self.values[0]
        await interaction.response.send_message(
            f"✅ Đã chọn: **{self.values[0]}**",
            ephemeral=True
        )


class ToolView(discord.ui.View):
    def __init__(self, owner, filename, original, bones):
        super().__init__(timeout=600)
        self.owner = owner
        self.filename = filename
        self.original = original
        self.bones = bones
        self.selected = None
        self.result = None

        self.add_item(FunctionSelect())

    async def interaction_check(self, interaction):
        if interaction.user.id != self.owner:
            await interaction.response.send_message(
                "❌ Đây không phải phiên làm việc của bạn.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(
        label="▶ XỬ LÝ FILE",
        style=discord.ButtonStyle.primary
    )
    async def run_button(self, interaction, button):
        if not self.selected:
            await interaction.response.send_message(
                "⚠️ Hãy chọn chức năng trước!",
                ephemeral=True
            )
            return

        function = self.selected

        if function.startswith("scale") or function == "moveFull":
            await interaction.response.send_modal(
                ValueModal(self, function)
            )
        else:
            await self.run_function(interaction, function)

    @discord.ui.button(
        label="📥 LƯU / NHẬN FILE",
        style=discord.ButtonStyle.success
    )
    async def download_button(self, interaction, button):
        if self.result is None:
            await interaction.response.send_message(
                "⚠️ Bạn chưa xử lý file!",
                ephemeral=True
            )
            return

        file = discord.File(
            io.BytesIO(self.result),
            filename=self.filename
        )

        await interaction.response.send_message(
            "✅ FILE ĐÃ XỬ LÝ XONG!",
            file=file,
            ephemeral=True
        )

    async def run_function(self, interaction, function, value=None):
        try:
            result, changed = await asyncio.to_thread(
                process_data,
                self.original,
                self.bones,
                function,
                value
            )

            self.result = result

            await interaction.response.send_message(
                f"✅ **XỬ LÝ THÀNH CÔNG**\n"
                f"Chức năng: `{function}`\n"
                f"Số bone xử lý: `{changed}`\n"
                f"Nhấn **LƯU / NHẬN FILE** để lấy file.",
                ephemeral=True
            )

        except Exception as error:
            await interaction.response.send_message(
                f"❌ Lỗi xử lý: `{error}`",
                ephemeral=True
            )


class VCBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()


intents = discord.Intents.default()
bot = VCBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"VC UMA BONE PRO ONLINE: {bot.user}")


@bot.tree.command(
    name="uma",
    description="Mở VC UMA BONE PRO"
)
async def uma(interaction: discord.Interaction, file: discord.Attachment):
    filename = file.filename

    if not FILE_PATTERN.fullmatch(filename):
        await interaction.response.send_message(
            "❌ Tên file không đúng định dạng!\n"
            "Yêu cầu: `assetindexer.xxx`",
            ephemeral=True
        )
        return

    if file.size > MAX_SIZE:
        await interaction.response.send_message(
            "❌ File vượt quá giới hạn 20MB!",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        original = await file.read()
        bones = await asyncio.to_thread(parse_binary, original)

        if not bones:
            await interaction.followup.send(
                "❌ Không tìm thấy bone trong file.",
                ephemeral=True
            )
            return

        view = ToolView(
            interaction.user.id,
            filename,
            original,
            bones
        )

        embed = discord.Embed(
            title="⚡ VC UMA BONE PRO",
            description=(
                "━━━━━━━━━━━━━━━━━━\n"
                "📂 File đã nhận thành công\n"
                f"📄 `{filename}`\n"
                f"🦴 Bone tìm thấy: `{len(bones)}`\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Chọn chức năng bên dưới để xử lý."
            ),
            color=0x00BFFF
        )

        await interaction.followup.send(
            embed=embed,
            view=view,
            ephemeral=True
        )

    except Exception as error:
        await interaction.followup.send(
            f"❌ Không đọc được file: `{error}`",
            ephemeral=True
        )


if not TOKEN:
    raise SystemExit("Chua nhap Discord Bot Token!")

bot.run(TOKEN)