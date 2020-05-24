<?xml version="1.0" encoding="UTF-8"?>
<!-- Copy all
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="    text()|@*    ">
    <xsl:value-of select="."/>
  </xsl:template>
</xsl:stylesheet> 
--><!--<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">--><!--    <xsl:output method="txt" indent="yes"/>--><!----><!--    <xsl:template match="@*|node()">--><!--        <xsl:copy>--><!--            <xsl:apply-templates select="@*|node()"/>--><!--        </xsl:copy>--><!--    </xsl:template>    --><!--    <xsl:template match="TotalNumberStations">--><!--    <TAG>--><!--            <xsl:apply-templates />--><!--    </TAG>  --><!--    </xsl:template>--><!--    <xsl:template match="Source"/> --><!--Only network level--><!--    <xsl:template match="*|@*|text()">--><!--        <xsl:copy>--><!--            <xsl:apply-templates select="@*"/>--><!--        </xsl:copy>--><!--    </xsl:template>--><!--<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">--><!--<xsl:output method="html" indent="yes"/>--><!--<xsl:template match="/">--><!--<html>--><!--<head>--><!--<title>Error</title>--><!--</head>--><!--<body>--><!--<h1>Item overview</h1>--><!--<ul>--><!--<xsl:for-each select="//*">--><!--<li>--><!--<xsl:value-of select="."/>--><!--</li>--><!--</xsl:for-each>--><!--</ul>--><!--</body>--><!--</html>--><!--</xsl:template>--><!--</xsl:stylesheet>--><!--NOT WORKING--><!--<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">--><!--<xsl:output method="text" omit-xml-declaration="yes" indent="no"/>--><!--<xsl:template match="/">--><!--<html>--><!--<xsl:for-each select="//*">--><!--<xsl:value-of select="@name"/>--><!--<xsl:value-of select="."/>--><!--    --><!--</xsl:for-each>--><!--</html>--><!----><!--</xsl:template>--><!--</xsl:stylesheet>-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output omit-xml-declaration="yes" indent="yes"/>
    <xsl:output method="text"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="*">
        <xsl:apply-templates select="node()|@*"/>
        <xsl:text> </xsl:text>
    </xsl:template>
<!---->
<!--    <xsl:template match="Error">-->
<!--       at -f <xsl:apply-templates select="*|@*"/>-->
<!--    </xsl:template>-->
</xsl:stylesheet>