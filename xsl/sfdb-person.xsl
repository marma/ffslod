<?xml version="1.0"?> 
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
		xmlns:schema="https://schema.org/">

	<xsl:param name="uri"/>

	<xsl:template match="/">
		<rdf:Description>
			<xsl:attribute name="rdf:about"><xsl:value-of select="$uri"/></xsl:attribute>
			<xsl:apply-templates/>
		</rdf:Description>
	</xsl:template>

	<xsl:template match="html/body/main/header/div[@class='page-header__info']">
		<schema:name><xsl:value-of select="h1[@class='page-header__heading']"/></schema:name>

		<xsl:for-each select="div[@class='page-header__meta']/*">
			<xsl:choose>
				<xsl:when test="@class='person__born'">
					<schema:birthDate><xsl:value-of select="."/></schema:birthDate>
				</xsl:when>
				<xsl:when test="@class='person__death'">
					<schema:deathDate><xsl:value-of select="."/></schema:deathDate>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template>

	<!--xsl:template match="ul[@class='link-list']a-->
</xsl:stylesheet>

