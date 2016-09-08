import base64
import gzip
import json

payload = r'''
+,^C)S"S/1!rqYTD%=E*%#1skm&ukbId:!m-SaI`d;?6!ecB9M6iMm;#c%$gZolJuGqEn[)Qd6\n
I0N/SEU6_[ZTfEA]2%I=iaq*hf/UX(U^+0$am/K,\md<<#P[sl,jrGXSVI@oo*=`=\fUI5*#>iL:
!B+LP&3HQ`p/g56$h<_`=7Q7P&96ip:10G#@hqG)Neg,9,Z5ZMp0*RO-Y(GUF0!]e(r0BIbg/<+s
;#$tC,BbNlh9k[e'\,dNg.,!02BPfopecFJFNL?p+oP1O[[nsX-@OF;_RjL*rh,oao)W6n_6$2Wd
MTo25RX^-5/hs[QS?'2]KY&F`'l&(8GMcW!Mb<!8QFs`"3X:6aaRr+[<5'mL%bJVCMot-]O):p!S
ZH`LO>V>Ec5\:kT5V+\'(^(R%:'O"<N*+j`H,9OFj3J?,YNH9UOg0p)(]XO
'''

payload = json.loads(gzip.decompress(base64.a85decode(payload)).decode())
