<?php
ini_set('display_errors', 1);
include('db.php');
date_default_timezone_set('Europe/Helsinki');

if(isset($_GET['functionname']))
	$functionname = $_GET['functionname'];

if(isset($_GET['arguments']))
	$args = $_GET['arguments'];


$db = DbOpen('db');
if(!$db)
{
	echo "DbOpen failed";
	exit;
}

//MYSQL
/*if ($functionname == "getlocations") {
	$q = "SELECT DISTINCT location FROM sitings";

	$data = DbQuery($db, $q);

	echo json_encode($data);
}*/
//PSQL
if ($functionname == "getlocations") {
	$q = "SELECT DISTINCT ON (\"LOCATION\") \"LOCATION\" FROM sitings";

	$data = DbQuery($db, $q);

	echo json_encode($data);
}


//Get Site Names and BTS_ID by Location
if ($functionname == "getsites") {
	
	if ($args == "all" or $args === NULL) {
		$q = "SELECT * FROM sitings";
	} else {
		//$q = "SELECT* FROM sitings WHERE LOCATION = '" .$args. "'"; //MYSQL
		$q = "SELECT* FROM sitings WHERE \"LOCATION\" = '" .$args. "'"; //PSQL
	}
	
	$data = DbQuery($db, $q);
	echo json_encode($data);
}

//For testing purposes
if ($functionname == "echosites") {
	
	$q = "select BTS_ID,FIELD_NAME, Value from sites where BTS_ID =".$args."";
	
	$data = DbQuery($db, $q);
	echo json_encode($data);
}

//Get column names
if ($functionname == "getcolumnnames") {

	//$q = "select column_name from information_schema.columns where table_schema = 'site_list' and table_name = 'sitings'"; //MYSQL
	$q = "select column_name from information_schema.columns where table_name = 'sitings'"; //PSQL
	
	$data = DbQuery($db, $q);
	echo json_encode($data);
 }

//Get all info for one site
if ($functionname == "getsiteinfo") {

	$q = "SELECT * FROM (SELECT * FROM sites WHERE BTS_ID=".$args.") T1 RIGHT OUTER JOIN template ON (T1.FIELD_NAME = template.FIELD_NAME) ORDER BY ROW_NUM ASC";
	
	$data = DbQuery($db, $q);
	echo json_encode($data);
}

//Search for a site
if ($functionname == "searchsite") {
	
	//PSQL
	if ($args[0] == "BTS_ID") {
		$q = "SELECT * FROM sitings WHERE \"" .$args[0]. "\"= ".$args[1];
	} else {
		$q = "SELECT * FROM sitings WHERE \"" .$args[0]. "\" LIKE '%" .$args[1]."%'";
	}
	
	$data = DbQuery($db, $q);
	echo json_encode($data);
}

//Search for a site
if ($functionname == "deletesite") {

	$q = "DELETE FROM sitings WHERE \"BTS_ID\" =" .$args;
	
	$data = DbDelete($db, $q);
	echo json_encode("success");
}

//Save new or updated site into DB
if ($functionname == "savesite") {

    $arguments = json_decode($args,true);
    $siteinfo = $arguments["objArray"];
    
    if ($arguments["saveMode"]["mode"] == "new") {

        $sitedb_new = "INSERT INTO sitings (";
		$sitedb_values = "VALUES (";
		
        foreach ($siteinfo as $key => $val) {
            if ($key == "BTS_ID") {
                //CHECK IF THERE IS ALREADY THIS BTS IN DATABASE, when adding a new site
                $q = "SELECT * FROM sitings WHERE \"BTS_ID\" = ".$val;
                $data = DbQuery($db, $q);
                if (!empty($data)) {
                    echo json_encode("DUPLICATE_BTS");
                    return;
                }
            } else if ($key == "BTS_IP") {
                //CHECK IF THERE IS ALREADY THIS BTS IP IN DATABASE, when adding a new site
                $q = "SELECT * FROM sitings WHERE \"BTS_IP\" = ".$val;
                $data = DbQuery($db, $q);
                if (!empty($data)) {
                    array_unshift($data,"iperr");
                    echo json_encode($data);
                    return;
                }
            } else if ($key == "LAST_EDITED") {
                $val = date("Y-m-d H:i:s", strtotime("33 minutes"));
            }
            if (!empty($val)) {
                //$sitedb_new .= "\"$key\" = '$val',";
				$sitedb_new .= "\"$key\",";
				if ($key == "BTS_ID") {
					$sitedb_values .= "$val,";
				} else {
					$sitedb_values .= "'$val',";
				}
			}
        }
		
		$sitedb_new[strlen($sitedb_new)-1] = ")";
		$sitedb_new .= " ";
		$sitedb_values[strlen($sitedb_values)-1] = ")";
		$sitedb_values .= ";";
		
        DbInsert($db, $sitedb_new.$sitedb_values);
        
    } else if ($arguments["saveMode"]["mode"] == "update") {
    
        $sitedb_upd = "UPDATE sitings SET ";
        
        foreach ($siteinfo as $key => $val) {
            if ($key == "BTS_ID") {
                $btsid = $val;
                continue;
            } else if ($key == "BTS_IP") {
                //CHECK IF THERE IS ALREADY THIS BTS IP IN DATABASE, when updating old site
                $q = "SELECT * FROM sitings WHERE \"BTS_IP\" = ".$val;
                $data = DbQuery($db, $q);
                if (!empty($data)) {
                    if ($data[0]["BTS_ID"] != $btsid) {                    
                        array_unshift($data,"iperr");
                        echo json_encode($data);
                        return;   
                    }
                }
            } else if ($key == "LAST_EDITED") {
                $val = date("Y-m-d H:i:s", strtotime("33 minutes"));
            }
            if (!empty($val)) {
                $sitedb_upd .= "\"$key\" = '$val',";
            }
        }
        $sitedb_upd[strlen($sitedb_upd)-1] = " ";
        $sitedb_upd .= "WHERE \"BTS_ID\" =".$btsid;
        
        DbUpdate($db, $sitedb_upd);
    }
}

$db = null;

?>

