sed -E "s/:.//g" $1 | tr '\n' '~' | sed -E "s/~~/\n/g" | tr '~' '\t'
