# Проверка pkglist.txt по дереву Portage: есть ли пакет и виден ли он (keywords/лицензия/маска).
# Запуск внутри chroot: python3 check-atoms.py pkglist.txt
import sys
import portage

db = portage.db[portage.root]["porttree"].dbapi
section, bad = "?", 0
for raw in open(sys.argv[1], encoding="utf-8"):
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("["):
        section = line.strip("[]")
        continue
    atom = line.split()[0]
    cps = db.cp_list(portage.dep.dep_getkey(atom))
    if not cps:
        print(f"MISSING  [{section}] {atom}")
        bad += 1
    elif not db.xmatch("bestmatch-visible", atom):
        why = portage.getmaskingstatus(cps[-1], portdb=db)
        print(f"MASKED   [{section}] {atom}  {cps[-1]}: {', '.join(why)}")
        bad += 1
    else:
        print(f"ok       [{section}] {db.xmatch('bestmatch-visible', atom)}")
print(f"problems: {bad}")
