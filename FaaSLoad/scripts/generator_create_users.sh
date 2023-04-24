#!/usr/bin/env bash

# Output directory where authentication tokens of generated users are written
AUTHKEY_DIR="../generator_users"
# Path to the wskadmin executable
WSKADMIN="../../openwhisk/bin/wskadmin"
# FaaSLoad database name
FAASLOAD_DB=faasload
# FaaSLoad user name for DB access
FAASLOAD_DBUSER=faasload

echo "Create OpenWhisk users for FaaSLoad's generator mode"
echo "This script reads the list of actions to use in the dataset generation from FaaSLoad's database."
echo "You must have already loaded the actions in the table \`functions\` of the database \`faasload\`."
echo
echo "FaaSLoad database: \`$FAASLOAD_DB\`; DB user name: \"$FAASLOAD_DBUSER\"."
echo "The directory containing the authentication tokens is \"$(realpath "$AUTHKEY_DIR")\"."
echo "In \"loader.yml\", set \`openwhisk:authkeys\` to this path."
echo

mkdir -p "$AUTHKEY_DIR"

mysql -u $FAASLOAD_DBUSER $FAASLOAD_DB -BNe 'SELECT `name` FROM `functions`;' |\
while read -r fn; do
    user="user-${fn#*/}"

    echo "Creating user \"$user\"..."

    "$WSKADMIN" user create "$user" > "$AUTHKEY_DIR"/"$user"
done

echo
echo "Done!"