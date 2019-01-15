<?php
//Setup Web Service
$words = $argv[1];
$person = $argv[2];
$vol = intval($argv[3]);
$speed = intval($argv[4]);
$client = new SoapClient("http://tts.itri.org.tw/TTSService/Soap_1_3.php?wsdl");
// Invoke Call to ConvertText
$result=$client->ConvertText("doctor","doctor",$words,$person,$vol, $speed, "wav");
// Iterate through the returned string array
$resultArray= explode("&",$result);
list($resultCode, $resultString, $resultConvertID) = $resultArray;
echo "resultCode：".$resultCode."\n";
echo "resultString：".$resultString."\n";
echo "resultConvertID：".$resultConvertID."\n";

sleep(2);
$result1=$client->GetConvertStatus("doctor","doctor", intval($resultConvertID));
// Iterate through the returned string array
$resultArray1= explode("&",$result1);
list($resultCode, $resultString, $statusCode, $status, $resultUrl) = $resultArray1;
echo "resultCode：".$resultCode."\n";
echo "resultString：".$resultString."\n";
echo "statusCode：".$statusCode."\n";
echo "status：".$status."\n";
echo "resultUrl：".$resultUrl."\n";

file_put_contents("word.wav", file_get_contents($resultUrl));
?>
