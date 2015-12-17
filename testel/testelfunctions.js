/*
TODO:

*/


$( document ).ready(function() {
	
	$.get( "dbquery.php", { functionname: "getlocations", arguments: 1 } )
		.done(function( data ) {
			data = JSON.parse(data);
			for (var i = 0; i < data.length ; i++ ) {
				$( "#siteselect" ).append("<option value='"+data[i].LOCATION+"'>"+data[i].LOCATION+"</option>");
			}
	});
	
	$( "#siteselect" ).change(function () {
		getsites(this)
	  });

	$( "#searchForm" ).submit(function( event ) {
		searchSite($( "#searchCategory" ).val(),$( "input:first" ).val());
		event.preventDefault();
	});
	
	$("#dialog").dialog({
      autoOpen: false,
	  height: 700,
      width: 700,
	  modal: true,
    });
 
    $("#opener").click(function() {
		loadIPandParameters();
	
      $("#dialog").dialog( "open" );
    });
	
});

function getsites(arg) {
	$.get( "queryfunctions_testel.php", { functionname: "getsites", arguments: arg.value } )
	  .done(function( data ) {
		printSites(JSON.parse(data));
	});
}

function searchSite(searchCat,searchWord) {
	$.get( "queryfunctions_testel.php", { functionname: "searchsite", arguments: [searchCat,searchWord] } )
	  .done(function( data ) {
        printSites(JSON.parse(data));
	  });
}

// #Fill the view with sites in DB
function printSites(data) {
    $( "#sites" ).empty();
	$( "#ips" ).empty();

    for (var i = 0; i < data.length ; i++ ) {
			row = "<div class='heading' id="+data[i].BTS_ID+">"+data[i].BTS_ID+" - "+data[i].BTS_NAME+"</div>";
			row += "<div class='content' style='display: none;'><ul class='detailstyle'>";

			for (var prop in data[i]) {
				if (prop == "BTS_ID") {
					row += "<li class='ui-state-default'><span/><p>"+prop+"</p><p>"+data[i][prop]+"</p></li>";
				} else if (prop == "LAST_EDITED") {
                    row += "<li class='ui-state-default'><span/><p>"+prop+"</p><p>"+data[i][prop]+"</p></li>";
                } else { 
					row += "<li class='ui-state-default'><span/><p>"+prop+"</p><input class='siteinput' type='text' value='"+data[i][prop]+"'></li>";
				}
			}
			row += "<li><button onclick='saveSite(this)'>Save changes</button><button onclick='deleteSite(this)'>Delete site</button></li>";
			row += "</ul></div>";
			$( "#sites" ).append(row);
		}
		
		$(".heading").click(function() {
				$(this).next(".content").slideToggle(500);
		});
}

// #Delete site from DB with a confirmation
function deleteSite(t) {

    var rows = $(t.parentElement).siblings();
    var answer = window.prompt('Delete site with ID: '+rows[0].children[2].innerHTML+'? (write "delete" and press OK)');
	
	if (answer == "delete") { 
		$.get( "queryfunctions_testel.php", { functionname: "deletesite", arguments: rows[0].children[2].innerHTML } )
		  .done(function( data ) {
			data = JSON.parse(data);
			if (data == "success") {
				alert("Site deleted from database");
			} 
			window.location.reload();
		});
	}
}

function createCollapse() {
	//Initially hide all the expandable content with class name "content" 
	$(".collapseData").hide();

	//Toggle the component when parent class "heading" is clicked on 
	$(".collapse").click(function() {

		var header = $(this);

		//Expand or collapse the content with slide mode animation 
		header.next(".collapseData").slideToggle(500);
	});
}

// #Make new site.
// #Clear view and make new site view.
function newSite(t) {

	$("#sites").empty();
	$("#ips").empty();
	$("#siteselect").val("Select Site Location");
	
	row = "<div class='heading'>NEW SITE</div>";
	row += "<div class='content'><ul class='detailstyle'>";
	
	$.get( "queryfunctions_testel.php", { functionname: "getcolumnnames" } )
	  .done(function( data ) {
		data = JSON.parse(data);
		for (var i = 0; i < data.length ; i++ ) {
			if (data[i].column_name == "LAST_EDITED") {
                row += "<li class='ui-state-default'><span/><p>"+data[i].column_name+"</p><p>Date and Time</p></li>";
            } else {
				row += "<li class='ui-state-default'><span/><p>"+data[i].column_name+"</p><input class='siteinput' type='text' value=''></li>"; //Critical, if UI changes are made	
			}
		}
		
		row += "<li><button onclick='saveSite(this)'>Save new site</button></li>";
		row += "</ul></div>";
		$( "#sites" ).append(row);
	});
}

// #Crawl through the html and parse new and updated info for site
// #Save new info to DB
function saveSite(t) {
	
	var rows = $(t.parentElement).siblings();
	var objName = "";
	var objValue = "";
	myJson={objArray:{},saveMode:{}};
	
	//Flag for the php script
	if (t.innerHTML == "Save new site") {
		myJson.saveMode["mode"] = "new";
		
		for (var i = 0; i < $(t.parentElement).siblings().length ; i++) {
			if (rows[i].children[1].innerHTML.match("BTS_ID|BTS_NAME|BTS_IP") && rows[i].children[2].value.length == 0) {
				alert("Missing BTS ID, BTS NAME or BTS IP");
				return;
			} else if (rows[i].children[1].innerHTML.match("LOCATION") && rows[i].children[2].value.length == 0) {
				rows[i].children[2].value = "n/a";
			}
			objName = rows[i].children[1].innerHTML;
			objValue = rows[i].children[2].value;
			
			myJson.objArray[objName]=trimwhitespace(objValue);
		}
	} else {
		myJson.saveMode["mode"] = "update";
		
		for (var i = 0; i < $(t.parentElement).siblings().length ; i++) { 
			if (rows[i].children[1].innerHTML.match("BTS_ID|LAST_EDITED")) {
				objName = rows[i].children[1].innerHTML;
				objValue = rows[i].children[2].innerHTML;
			} else {
				if (rows[i].children[1].innerHTML.match("BTS_IP|BTS_NAME") && rows[i].children[2].value.length == 0) {
					alert("Missing BTS ID, BTS NAME or BTS IP");
					return;
				}
				objName = rows[i].children[1].innerHTML;
				objValue = rows[i].children[2].value;
			}
			myJson.objArray[objName]=trimwhitespace(objValue);
		}
	}

	$.get( "queryfunctions_testel.php", { functionname: "savesite" , arguments: JSON.stringify(myJson)})
		.done(function( data ) {
        data = JSON.parse(data);
		if (data == "DUPLICATE_BTS") {
			alert("Already a site in database with given BTS_ID");
		} else if(data[0] == "iperr") {
            alert("A site with IP: "+data[1].BTS_IP+" already exists. New site was not added to the database.");
        }
	});
	if (myJson.saveMode["mode"] == "new") {
		alert("New site saved to database");
		window.location.reload();
	} else {
		alert("Site information updated to database");
	}
}

//Trims whitespace from beginning and end of the string
function trimwhitespace (str) {
	if (typeof str == 'undefined') {
		return "";
	}
    return str.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function offFocus(e) {
	if (!this.innerHTML) {
		this.innerHTML = "NULL";
	}
}

