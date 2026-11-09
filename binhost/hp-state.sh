#!/bin/bash
# Снимок настроек Portage с HP для сборки бинхоста: запускать на ноуте после emerge-webrsync
# или правок /etc/portage, потом закоммитить папку binhost/.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf portage && mkdir portage
for f in make.conf package.use package.accept_keywords package.license package.mask; do
  [ -e "/etc/portage/$f" ] && cp -r "/etc/portage/$f" portage/
done
cp /var/lib/portage/world world   # для сборки с update_world: тот же набор пакетов, что на HP
cp /var/db/repos/gentoo/metadata/timestamp.chk portage-timestamp
readlink /etc/portage/make.profile | sed 's|.*/profiles/||' > profile
echo "дерево: $(cat portage-timestamp), профиль: $(cat profile)"
