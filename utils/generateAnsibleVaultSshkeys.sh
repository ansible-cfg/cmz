#!/bin/bash

function usage() {
  cat <<Usage

  $(basename $0) [-h --help] accountname1 .. accountnameN

  This script generates 4096bit RSA SSH key pairs for each
  accountname given as an argument.
  The accountname becomes the comment of the public key.

  It prints the generated keys to STDOUT as a YAML dictionary.
  The accountnames are the dictionary keys.

  The format is suitable to add the keys into a
  Commerce Cloud v1.2 management zone Ansible vault file.

  Example:
  $(basename $0) "svc_ansible" "svc_ytr" "svc_portal2ssh" "svc_portal2ad" \
  "svc_rundeckdeploy" "svc_rundeck2ad" "sshkey_cmdbbckp" "sshkey_scm"
  Create a ssh key pair for each of the service users.




Usage
}

# Commandline parsing:
declare -a args=()
while [ $# -gt 0 ]
do
    case $1 in
      --help|-h)    usage; exit 0 ;;
      --*|-*)       usage; echo -e "Unknown option $1\n"; exit 1 ;;
      *)            args=("${args[@]}" "$1"); shift ;;
    esac
done

declare -i nrarg=${#args[@]}
if [ $nrarg -lt 1 ]
then
    usage;
    echo -e "\nI need at least one account name.\n"
    exit 1
else
    para=${args[0]}
fi


# Start working:
dir='./sshgentemp'
if [ -d $dir ]
then
    echo "My temporary work directory $dir already exists."
    echo "Check and remove it manually first."
    exit 1
else
    mkdir $dir
fi

for acc in "${args[@]}"
do
    ssh-keygen -q -b 4096 -t rsa -C "$acc" -N '' -f $dir/k
    echo "svc_users_vault_""$acc""_privateKey: |"
    sed -e 's/^/  /g' $dir/k
    echo
    echo "svc_users_vault_""$acc""_publicKey: >"
    sed -e 's/^/  /g' $dir/k.pub
    echo
    echo
    rm -f $dir/k $dir/k.pub
done

rm -rf $dir
