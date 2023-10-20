<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ingv="http://www.fdsn.org/xml/station/ingv" xmlns:x="http://www.fdsn.org/xml/station/1" version="3.0">
<xsl:strip-space elements="*"/>
<xsl:output method="text" media-type="application/json" indent="no"/>

<xsl:template match="x:ERROR">
    <xsl:value-of select="."/>
</xsl:template>


<!--<xsl:template match="x:FDSNStationXML">{"type":"FeatureCollection","features":[<xsl:apply-templates><xsl:sort select="@code"/></xsl:apply-templates>]}</xsl:template>-->

<xsl:template match="x:FDSNStationXML">
<xsl:text>{"type":"FeatureCollection","features":[</xsl:text>
<xsl:for-each select="x:Network">
<!--Comma before, skip the first-->
<xsl:if test="position() != 1">,</xsl:if>
                <xsl:apply-templates/>
            </xsl:for-each>
<xsl:text>]}</xsl:text>
</xsl:template>

<!--Matching and sorting for station code-->
<xsl:template match="x:Network">
    <xsl:apply-templates>
        <xsl:sort select="@code"/>
    </xsl:apply-templates>
</xsl:template>

<!--A feature for every station line-->
<xsl:template match="x:Station">
<xsl:text>{"type":"Feature","properties":{"code":"</xsl:text>
<xsl:value-of select="@code"/>
<xsl:text>","Name":"</xsl:text>
<xsl:value-of select="x:Site"/>
<xsl:text>","network":"</xsl:text>
<xsl:value-of select="../@code"/>
<xsl:text>","startDate":"</xsl:text>
<xsl:value-of select="@startDate"/>
<xsl:text>","endDate":</xsl:text>
<xsl:choose>
    <xsl:when test="@endDate">"<xsl:value-of select="@endDate"/>"</xsl:when>
    <xsl:otherwise>null</xsl:otherwise>
</xsl:choose>
<xsl:text>,"Latitude":</xsl:text>
<xsl:value-of select="x:Latitude"/>
<xsl:text>,"Longitude":</xsl:text>
<xsl:value-of select="x:Longitude"/>
<xsl:text>,"Elevation":</xsl:text>
<xsl:value-of select="x:Elevation"/>
<xsl:text>},"geometry":{"type":"Point","coordinates":[</xsl:text>
<xsl:value-of select="x:Longitude"/>
<xsl:text>,</xsl:text>
<xsl:value-of select="x:Latitude"/>
<xsl:text>]}}</xsl:text>
<xsl:apply-templates/></xsl:template>


<!--  Catch all -->
<xsl:template match="text()|@*"></xsl:template>


</xsl:stylesheet>
