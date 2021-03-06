#!e:\perl\bin\perl
#
# Brian Dietz 
# brian.dietz@caremark.com
#
# (Changed by Steve Shipway to put all telnet code into mypage() function)

use strict;
use CGI;
use Net::SNMP;
use Net::Telnet::Cisco;
# Variables, you must define EVERY variable, because of the use strict.
my( $device, $community, $targetwindow, $target, $file, $backurl )
	= ( "","public","graph","","","");
# Change the follwoing to your password and enablepass.
my ($password, $enablepass) = ('password', 'enablepass');

my( $conffile, $ifno, $routersurl, $ifname );
my( $q ) = new CGI;
my( %headeropts );
my( $thishost ) = $q->url();
my( $refresh  ) = 'javascript:parent.graph.location.reload(true)';
$thishost =~ /http:\/\/([^\/]+)\//;
$thishost = $1;


#######################################################################

# Process parameters
$device       = $q->param('h') if(defined $q->param('h'));
$file         = $q->param('fi') if(defined $q->param('fi'));
$target       = $q->param('ta') if(defined $q->param('ta'));
$community    = $q->param('c') if(defined $q->param('c'));
$ifno         = $q->param('ifno') if(defined $q->param('ifno'));
$backurl      = $q->param('b') if(defined $q->param('b'));
$targetwindow = $q->param('t') if(defined $q->param('t'));
$conffile     = $q->param('conf') if(defined $q->param('conf'));
$routersurl   = $q->param('url') if(defined $q->param('url'));
$routersurl   = "http://$thishost/cgi-bin/routers2.cgi" if(!$routersurl);
$ifname = $target;
$ifname =~ s/$device\_// ;
$ifname =~ s/_/\// ;

#   CGI parameters:
#	fi = MRTG .cfg file name
#	ta = MRTG target name
#	c = Community string (potential security risk)
#	h = host name
#	ifno = interface number, if appropriate
#	t = HTTP target page object name
#	b = a URL that will take you back to the routers.cgi screen
#	conf = The filename of the routers2.conf configuration file
#	url = The URL of the routers.cgi script


# At this point, you may wish to add code to parse the $conffile file, and
# retrieve information shuch as the confpath parameter, or to read the
# MRTG file $file and retrieve the configuration for target $target
#



#######################################################################
# Put your page generation code in here.  HTTP headers already produced.
# The Javascript linked in the start_html function manages the side menu(s).
# Although the javascript is not required, it makes the menus update
# correctly after this option has been selected.

sub mypage()
{
	my( $javascript ) = "function RefreshMenu()
	{
	var mwin; var uopts;
	mwin = parent.menu;
	uopts = 'T';
	if( parent.menub ) { mwin = parent.menub; uopts = 't'; }
	mwin.location = '".$routersurl."?if=__none&rtr="
		.$q->escape($file)."&page=menu&xmtype=options&uopts='+uopts;
	}";

	print $q->start_html({-title=>"Interface Information",
		-script=>$javascript, -onLoad=>"RefreshMenu()"});

	print $q->h1("Interface Information");

my $telnet = Net::Telnet::Cisco->new(Host => "$device");
# Login to the box
$telnet->login(Password => $password);
# Enter enable mode
$telnet->enable("$enablepass");
# run the command
my @output;
@output = $telnet->cmd("show counters $ifname");

$telnet->close;

#This next line prints each line 1 at a time, instead of all in a row. Also, it removes the the = 0 lines (who cares if it's 0)
# also, it removes blank lines.
	foreach my $info (@output) {
	        if ($info =~ /(\=\s*0)/) {next} elsif ($info !~ /\S+/) {next} else {print "$info".$q->br."\n"}};
	print $q->hr."Return to ".$q->a({href=>$backurl},"Last Page").'  Or  '.$q->a({href=>$refresh},"Refresh Screen") if($backurl);
	print $q->end_html();
}


# HTTP headers
%headeropts = ( -expires=>"now" );
$headeropts{target} = $targetwindow if($targetwindow);
print $q->header(%headeropts);

# Make the page
mypage();

# End
exit(0);
