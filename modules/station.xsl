<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ingv="http://www.fdsn.org/xml/station/ingv" xmlns:x="http://www.fdsn.org/xml/station/1" version="1.0"> 
<xsl:strip-space elements="*"/>
 <xsl:output method="text" media-type="text/plain" indent="yes"/>
<xsl:template match="x:FDSNStationXML">
    <xsl:apply-templates/>
</xsl:template>

<!--   Network|Station|Latitude|Longitude|Elevation|SiteName|startDate|endDate-->
    <xsl:template match="x:Station">
      <xsl:value-of select="../@code"/>
      <xsl:value-of select="concat('|', @code, '|'  )"/>
      <xsl:value-of select="x:Latitude"/>
      <xsl:text>|</xsl:text>      
      <xsl:value-of select="x:Longitude"/>
      <xsl:text>|</xsl:text>      
      <xsl:value-of select="x:Elevation"/>  
      <xsl:text>|</xsl:text>      
      <xsl:value-of select="x:Site"/>  
      <xsl:text>|</xsl:text>           
      <xsl:value-of select="@startDate"/>
      <xsl:text>|</xsl:text>      
      <xsl:value-of select="@endDate"/>  

<!-- Next two lines to get newlines -->
<xsl:text>
</xsl:text>
   </xsl:template>

<!--  Catch all -->
<xsl:template match="text()|@*">
 </xsl:template>

</xsl:stylesheet>