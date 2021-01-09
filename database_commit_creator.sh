repo_url=$1
commit_id=$2
vulnerability_id=$4
source_path=$5
[ -d $vulnerability_id/$commit_id ] || mkdir -p $vulnerability_id/$commit_id
#if [ -f $source_path/changed-source-code.tar.gz ]
#then
#  timestamp=`cat $vulnerability_id/$commit_id/timestamp`
#  echo "{" > $vulnerability_id/$commit_id/metadata.json
#  echo "  \"repository\" : \"$repo_url\"," >> $vulnerability_id/$commit_id/metadata.json
#  echo "  \"timestamp\" : \"$timestamp\"," >> $vulnerability_id/$commit_id/metadata.json
#  echo "  \"commit_id\" : \"$commit_id\"" >> $vulnerability_id/$commit_id/metadata.json
#  echo "}" >> $vulnerability_id/$commit_id/metadata.json
#  rm $vulnerability_id/$commit_id/timestamp
#  return
#fi
clone_once $repo_url
repo_dir=$(folder_for_repo $repo_url)
timestamp=$(git -C $repo_dir show --no-patch --no-notes --pretty='%at' $commit_id)
echo "{" > $vulnerability_id/$commit_id/metadata.json
echo "  \"repository\" : \"$repo_url\"," >> $vulnerability_id/$commit_id/metadata.json
echo "  \"timestamp\" : \"$timestamp\"," >> $vulnerability_id/$commit_id/metadata.json
echo "  \"commit_id\" : \"$commit_id\"" >> $vulnerability_id/$commit_id/metadata.json
echo "}" >> $vulnerability_id/$commit_id/metadata.json
echo "dir=$repo_dir"
echo "pwd=`pwd`"
# cd repository
for F in $(git -C $repo_dir diff  --name-only  $commit_id^..$commit_id);
do
  echo "repo_dir=$repo_dir"
  echo "pwd=`pwd`"
  echo "Extracting file: $F"
  [ -d $vulnerability_id/$commit_id/before/$(dirname $F) ] || mkdir -p $vulnerability_id/$commit_id/before/$(dirname $F)
  [ -d $vulnerability_id/$commit_id/after/$(dirname $F) ] || mkdir -p $vulnerability_id/$commit_id/after/$(dirname $F)
  if ( git -C $repo_dir cat-file -e $commit_id~1:$F &> /dev/null )
  then
    git -C $repo_dir show $commit_id~1:$F > $vulnerability_id/$commit_id/before/$F
  fi
  if ( git -C $repo_dir cat-file -e $commit_id:$F &> /dev/null )
  then
    git -C $repo_dir show $commit_id:$F > $vulnerability_id/$commit_id/after/$F
  fi
done
