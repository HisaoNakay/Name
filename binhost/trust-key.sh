#!/bin/bash
# Доверить ключ бинхоста Хисао в связке Portage (/etc/portage/gnupg, её ведёт getuto) —
# тем же способом, каким getuto доверяет ключам Gentoo. Запуск от root; на HP и в CI одинаково.
set -euo pipefail
export GNUPGHOME=${PORTAGE_GNUPGHOME:-/etc/portage/gnupg}
KEY="$(dirname "$(readlink -f "$0")")/binhost-key.asc"
[ -s "$GNUPGHOME/mykeyid" ] || getuto
FPR=$(gpg --batch --show-keys --with-colons "$KEY" | awk -F: '/^fpr/{print $10; exit}')
gpg --batch --quiet --import "$KEY"
gpg --batch --yes --no-tty --passphrase-file="$GNUPGHOME/pass" --pinentry-mode loopback \
    --local-user "$(head -1 "$GNUPGHOME/mykeyid")" --quick-lsign-key "$FPR"
gpg --batch --quiet --check-trustdb
chmod ugo+r "$GNUPGHOME/trustdb.gpg"
gpgconf --kill all
LC_ALL=C gpg --batch --list-keys --list-options show-uid-validity "$FPR" | grep -q "^uid *\[ *full *\]" \
  || { echo "Ключ не стал доверенным"; exit 1; }
echo "Ключ бинхоста $FPR в связке Portage"
