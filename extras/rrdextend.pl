#!/usr/bin/perl 
#
# rrdextend.pl v1.1
#
# This script will take as a parameter an MRTG .cfg file, and will identify
# all the RRD files it generates.  It will then give you the option to extend
# these to double length, which will allow routers.cgi to show the 'yesterday'
# and 'last week' time periods.
#
# The old .rrd files will be moved to .rrd.old extension just in case!
#
# This script must have access to the rrdtool executable, and the perl
# libraries.
#
# This script is PUBLIC DOMAIN.  You can do what you like with it.
#
# Steve Shipway, June 2002 steve@cheshire.demon.co.uk
#
# Jun 2002: First version v1.0
# Jul 2002: v1.1: If rra[7] not found, only warning generated, not cancelled.

use strict;
use RRDs;
use File::Basename;

my( @rrdfiles );
my( $cfgfile, $rrdpath, $pathsep );
my( $rrd, $rrdinfo, $rra, $dir, $from, $rv );
my( $rrdtool ) = "rrdtool"; # rrdtool executable

$pathsep = "/";
$pathsep = "\\" if( $^O =~ /win|dos/i );

$cfgfile = $ARGV[0];
if(!defined $cfgfile or  ! -f $cfgfile) {
	print "Unable to open file '$cfgfile'\n" if($cfgfile);
	print "Usage: rrdextend <cfgfile>\n";
	exit 1;
}

print "Reading cfg file '$cfgfile'...\n";
open CFG, "<$cfgfile" or do {
	print "Unable to read file.\n";
	exit 1;
};
$rrdpath = "";
while ( <CFG> ) {
	/^\s*Workdir\s*:\s*(\S+)/i && do {
		$rrdpath = $1; $rrdpath =~ s/[\\\/\s]+$//; $rrdpath .= $pathsep;
		next;
	};
	/^\s*Target\[(\S+)\]/i && do { push @rrdfiles, $rrdpath.(lc $1)
		.".rrd"; next; };
}
close CFG;

if(! @rrdfiles ) {
	print "This file contains no Target[]s.\n";
	exit 1;
}

foreach $rrd ( @rrdfiles ) {
	$dir = dirname $rrd;
	chdir $dir;
	$from = basename $rrd;
	print "Processing file $from.... ";
	if( ! -f $rrd ) { print "does not exist.\n";next; }
	if( ! -r $rrd ) { print "not readable.\n";next; }
	$rrdinfo = RRDs::info($rrd);

	if( !defined $rrdinfo->{'ds[ds0].type'}
		or !defined $rrdinfo->{'ds[ds0].type'}) {
		print "not generated by MRTG.\n"; next; }
	
	if( ! defined $rrdinfo->{'rra[7].rows'}
		or defined $rrdinfo->{'rra[8].cf'}) {
		print "WARNING: unusual RRD file.\n"; }

	if( $rrdinfo->{'rra[0].rows'} > 800 ) {
		print "already extended.\n"; next; }

	foreach $rra ( 0...7 ) {
		last if(!$rrdinfo->{"rra[$rra].rows"});
		print "RRA $rra";
		$rv = 0xffff & (system $rrdtool,"resize",$from,$rra,"GROW",
			($rrdinfo->{"rra[$rra].rows"}*2));
		if($rv) {
			print "\n** ERROR **\nUnable to execute rrdtool!\n";
			exit 1;
		}
		$from = "tmp.rrd";
		if(! rename "resize.rrd", $from ) {
			print "\n** ERROR **\nUnable to rename temporary file.\n";
			exit 1;
		}
		print "\b\b\b\b\b      \b\b\b\b\b\b";
	}
	if(! rename $rrd, $rrd.".old" ) {
		print "\n** ERROR **\nUnable to backup old .rrd file!\n";
		exit 1;
	}
	rename $from, $rrd;
	print "Updated.\n";
}

