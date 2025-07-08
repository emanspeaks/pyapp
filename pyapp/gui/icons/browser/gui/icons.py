from pyapp.gui.icons.thirdparty.codicons import Codicons
from pyapp.gui.icons.thirdparty.codicons import names as codicon_names
from pyapp.gui.icons.iconfont import IconSpec
from pyapp.gui.icons.thirdparty.fa5.solid import names as fa5s_names
from pyapp.gui.icons.thirdparty.fa5.solid import Fa5_Solid


ConfigIcon = IconSpec.generate_iconspec(Codicons, codicon_names.json)
ProgramIcon = IconSpec.generate_iconspec(Fa5_Solid, fa5s_names.icons)
