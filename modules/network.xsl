<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ingv="http://www.fdsn.org/xml/station/ingv" xmlns:x="http://www.fdsn.org/xml/station/1" version="3.0"> 
<xsl:strip-space elements="*"/>
<xsl:output method="text" media-type="text/plain" indent="yes"/>

<xsl:template match="x:ERROR">
    <xsl:value-of select="."/>
</xsl:template> 


<xsl:template match="x:FDSNStationXML">
<xsl:text>#Network | Description | StartTime | EndTime | TotalStations
</xsl:text>
<!--Matching and sorting for network code-->
    <xsl:apply-templates>
        <xsl:sort select="@code"/>
    </xsl:apply-templates> 
</xsl:template>



<!-- Match networks elements extracting lines as in Network|Description|StartTime|EndTime|TotalStations  -->
<xsl:template match="x:Network">
  
    <xsl:value-of select="concat(@code, '|'  )"/>
    <xsl:value-of select="x:Description"/>
    <xsl:value-of select="concat('|', @startDate, '|', @endDate , '|')"/>
    <xsl:value-of select="x:TotalNumberStations"/>
<!-- Do not indent next two lines to get newlines -->
<xsl:text>
</xsl:text>
</xsl:template>

<!--  Catch all -->
<xsl:template match="text()|@*">
 </xsl:template>

</xsl:stylesheet>
