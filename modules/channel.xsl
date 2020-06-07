<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ingv="http://www.fdsn.org/xml/station/ingv" xmlns:x="http://www.fdsn.org/xml/station/1" version="1.0"> 
<xsl:strip-space elements="*"/>
 <xsl:output method="text" media-type="text/plain" indent="yes"/>
<xsl:template match="x:FDSNStationXML">
    <xsl:apply-templates/>
</xsl:template>

<!--   Network|Station|Location|Channel|
       Latitude|Longitude|Elevation|Depth|
       Azimuth|Dip|SensorDescription|Scale|
       ScaleFrequency|ScaleUnits|SampleRate|StartTime|EndTime-->


<!--  <Response>-->
<!--                    <InstrumentSensitivity>-->
<!-- Scale                          <Value>251652000</Value>-->
<!-- ScaleFrequency                 <Frequency>10</Frequency>-->

    <xsl:template match="x:Channel">
        <xsl:value-of select="../../@code"/>
        <xsl:text>|</xsl:text>              
        <xsl:value-of select="../@code"/>
        <xsl:text>|</xsl:text>              
        <xsl:value-of select="@locationCode"/>
        <xsl:value-of select="concat('|', @code, '|'  )"/>
        <xsl:value-of select="x:Latitude"/>
        <xsl:text>|</xsl:text>      
        <xsl:value-of select="x:Longitude"/>
        <xsl:text>|</xsl:text>      
        <xsl:value-of select="x:Elevation"/>  
        <xsl:text>|</xsl:text>     
        <xsl:value-of select="x:Depth"/>  
        <xsl:text>|</xsl:text>
        <xsl:value-of select="x:Azimuth"/>  
        <xsl:text>|</xsl:text>        
        <xsl:value-of select="x:Dip"/>  
        <xsl:text>|</xsl:text>        
        <xsl:value-of select="x:Sensor"/>  
        <xsl:text>|</xsl:text>           
        <xsl:apply-templates select="x:Response"/>  
        <xsl:text>|</xsl:text>
        <xsl:value-of select="x:SampleRate"/> 
        <xsl:text>|</xsl:text>         
        <xsl:value-of select="@startDate"/>
        <xsl:text>|</xsl:text>      
        <xsl:value-of select="@endDate"/>  

<!-- Next two lines to get newlines -->
<xsl:text>
</xsl:text>
   </xsl:template>
    <xsl:template match="x:Response">
            <xsl:apply-templates select="x:InstrumentSensitivity"/> 
   </xsl:template>

    <xsl:template match="x:InstrumentSensitivity">
        <xsl:value-of select="x:Value"/>
        <xsl:text>|</xsl:text>       
        <xsl:value-of select="x:Frequency"/>
        <xsl:text>|</xsl:text>    
        <xsl:value-of select="x:InputUnits"/>        
   </xsl:template>

<!--  Catch all -->
<xsl:template match="text()|@*">
 </xsl:template>

</xsl:stylesheet>