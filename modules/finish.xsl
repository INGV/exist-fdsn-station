<?xml version="1.0" encoding="UTF-8"?>
<!-- Copy all
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="    text()|@*    ">
    <xsl:value-of select="."/>
  </xsl:template>
</xsl:stylesheet> 
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
    <xsl:output method="xml" indent="yes"/>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>    



<!--    <xsl:template match="TotalNumberStations">-->
<!--    <TAG>-->
<!--            <xsl:apply-templates />-->
<!--    </TAG>  -->
        
<!--    </xsl:template>-->
<!--    <xsl:template match="Source"/> -->
<!--Only network level-->
<!--    <xsl:template match="*|@*|text()">-->
<!--        <xsl:copy>-->
<!--            <xsl:apply-templates select="@*"/>-->
<!--        </xsl:copy>-->
<!--    </xsl:template>-->
    

    
</xsl:stylesheet>