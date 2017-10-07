sed 's/call edu.stanford.nlp.sempre.overnight.SimpleWorld.//g' $1 | grep utterance | sed -E 's/^\s*\(utterance "//' | sed -E 's/"\)$//' | tr -s ' ' > $1_nl.txt
sed 's/call edu.stanford.nlp.sempre.overnight.SimpleWorld.//g' $1 | grep listValue | tr -s ' ' > $1_dcs.txt

paste $1_nl.txt $1_dcs.txt > $2

