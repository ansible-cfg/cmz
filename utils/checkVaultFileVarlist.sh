#!/bin/bash

function usage() {
  cat <<Usage

  $(basename $0) [OPTIONS]

    We declare variables defined in encrypted vault YAML files also in
    its non-encrypted YAML files, e.g. portal.vault.yml and portal.yml
    We do so for the sake of searchability.
    See http://docs.ansible.com/ansible/2.4/playbooks_best_practices.html#best-practices-for-variables-and-vaults

    This script checks if variables defined in an encrypted vault YAML file are
    also defined in its corresponding non-encrypted YAML file, e.g.
    if "middleware_security_user" is defined in both group_vars/all/portal.vault.yml
    and its correspondent playbooks/group_vars/all/portal.yml

    If not we print a message to STDOUT.

  OPTIONS:
    --help -h

Usage
}

if [[ $# -gt 0 ]]; then
  usage
  if [[ ${1} = '-h' || ${1} = '--help' ]]; then
    exit 0
  else
    exit 2
  fi
fi

if ! which ansible-vault &>/dev/null; then
  echo "Error: This check can be run only on the Ansible control server."
  exit 2
fi

# cd to the playbooks base dir so we can work with shorter paths
cd "$( dirname "${BASH_SOURCE[0]}" )/.."
echo "Checking $(pwd)/"

declare -i missing_count=0
#find "playbooks/group_vars" -type f -name "*vault*yml.info" | xargs rm -f
for vaultfile in $( find "playbooks/group_vars" -type f -name '*.vault.yml' -not -name '*service_users*.yml' )
do
  # find the corresponding non-encrypted file
  directory=$(dirname $vaultfile)
  correspondent_file="$directory"/$(basename $vaultfile .vault.yml)".yml"
  test -f "$correspondent_file" || continue
  echo -e "\n- $vaultfile  <-->  $(basename $correspondent_file):"

  # get all varialbe names from the encrypted vault file and see if they are defined in its unencrypted equivalent
  for variable in \
    $( ansible-vault --vault-password-file=.vault.sh view $vaultfile  | \
    grep ':' | grep -v '#' | awk 'BEGIN{ FS=":" } { print $1 }' )
  do
    if ! grep -q "$variable" "$correspondent_file"
    then
      echo "  Missing: $variable"
      (( missing_count++ ))
    fi
  done
done

echo

if [[ -z ${vaultfile} ]]; then
  echo "Error: No vault YAML files found?"
  exit 2
fi

if [[ $missing_count -gt 0 ]]; then
  echo -e "Found $missing_count missing properties.\n\nSee http://docs.ansible.com/ansible/2.4/playbooks_best_practices.html#best-practices-for-variables-and-vaults for reference."
  exit 1
fi

echo "OK"
exit 0
