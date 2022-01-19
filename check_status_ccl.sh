#/bin/bash
readarray -t hosts << EOF
AT5N4201
AT5N4202
KG3N4201
KG3N4202
SFEN4201
SFEN4202
SBEN4201
SBEN4202
PXYN4201
PXYN4202
PXYN4203
PXYN4204
PXYN4205
LIFN4201
LDRN4201
LDRN4202
EOF

for h in "${hosts[@]}"; do
	output=$(timeout 5 /opt/ngncc/ccl/pfscmd instance $h "status")
	if [ $? -ne 0 ]
	then
		echo "$h - BAD - connection timed out"
	else
		lines=$(wc -l <<< $output)
		if (( lines > 1 ))
		then
			echo "$h - OK - $lines lines in output"
		else
			echo "$h - BAD - $lines lines in output"
		fi
	fi
done
