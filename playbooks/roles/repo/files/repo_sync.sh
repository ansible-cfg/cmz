#!/bin/bash -

#declare -r email_to='strahinja.stankovic@sap.com,pierre-luc.orsini@sap.com,ahmed.elgenidy@sap.com,gregory.carpenter@sap.com,edgar.warnking@sap.com,w.rake@sap.com'
#declare -r email_to='petar.petrov@sap.com,edgar.warnking@sap.com'
declare -r out_tmp='/tmp/rsync.out.txt'
declare -r script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
declare -r private_key_file="/home/repo/.ssh/repo_sync"
declare -r rsync_dir='/var/www'  # No trailing slash
declare -r lock_file="${BASH_SOURCE[0]%.*}.progress"

### FUNCTIONS ###

die () {
  rc="${1}"
  shift
  printf "%s\n" "${@}"
  exit "${rc}"
}

now () { date +%s; }

seconds_since () {
  # Expects unix time as argument; missing argument is non-fatal
  [[ ${1} =~ ^-?[0-9]+$ ]] || { echo -n 'Unspecified'; return 1; }
  echo -n $(( $(now) - ${1} ))
}


unlock () {
  rm -f "${lock_file}"
}

lock () {
  [[ -f ${lock_file} ]] && die 13 "Lock file '${lock_file}' exists for pid $(cat '${lock_file}')"
  trap unlock EXIT
  echo $$ > "${lock_file}" || die 14 "Could not create '${lock_file}'"
}

### MAIN ###

# Check if we should really run
[[ $# -eq 1 && $1 == '-sync' ]] || {
  cat <<EOF
Usage: ${BASH_SOURCE[0]} -sync
This is supposed to be run by cron and will rsync ${rsync_dir} from Boston.
EOF
  exit 0
}

[[ -r ${private_key_file} ]] || die 11 "Cannot read ${private_key_file}"
[[ -w ${rsync_dir} ]] || die 12 "No write permissions for ${rsync_dir}"

lock
declare -ir time_begin=$(now)  # Mark begin time
declare -r report_header="Scheduled sync report from ${HOSTNAME}"
printf "${report_header}\n\n" >"${out_tmp}"
sudo rsync -azvP --delete -e "ssh -o StrictHostKeyChecking=no -i '${private_key_file}'" "repo@yms-p-ma-repo-001.hybrishosting.com:${rsync_dir}/*" "${rsync_dir}/" &>>"${out_tmp}"
rc=$?
printf "\nrsync exitcode ${rc}\n" >>"${out_tmp}"
printf "Finished in $(seconds_since ${time_begin}) second(s)\n" >>"${out_tmp}"
#printf "${report_header}\n\nrsync exitcode ${rc}.  See attached log file for details\n" | mail -s "${report_header}" -a "${out_tmp}" "${email_to}"
printf "Output in ${out_tmp}\n"

