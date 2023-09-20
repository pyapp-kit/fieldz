from dataclass_compat import fields
from ome_types.model import Pixels
from rich import print

f = {f.name: f for f in fields(Pixels)}
print(f["id"])
