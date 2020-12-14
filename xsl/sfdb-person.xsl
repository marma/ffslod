<?xml version="1.0"?> 
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:schema="https://schema.org/">
    <xsl:param name="uri"/>
    <xsl:param name="base">https://id.svenskfilmdatabas.se</xsl:param>

    <xsl:template match="/">
		<rdf:RDF>
            <rdf:Description rdf:about="{$uri}">
                <xsl:apply-templates select="html/body/main/header/div[@class='page-header__info']"/>
			    <xsl:apply-templates select="//h2[@id='biography']"/>
            </rdf:Description>

            <xsl:apply-templates select="//h2[@id='films']"/>
		</rdf:RDF>
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

    <xsl:template match="h2[@id='biography']">
        <schema:description>
            <xsl:for-each select="following-sibling::div[1]/div/p">
                <xsl:choose>
                    <xsl:when test="position()!=last()">
                        <xsl:value-of select="concat(., ' ')"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="."/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
        </schema:description>
    </xsl:template>

    <xsl:template match="h2[@id='films']">
        <xsl:for-each select="following-sibling::div[1]/div/table/tbody/tr">
            <xsl:variable name="type" select="th"/>
            <xsl:for-each select="td/ul/li">
                <rdf:Description>
                    <xsl:attribute name="about" namespace="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                        <xsl:call-template name="remap">
                            <xsl:with-param name="url" select="a/@href"/>
                        </xsl:call-template>
                    </xsl:attribute>
                    <rdf:type resource="https://schema.org/Movie"/>
                    <schema:name><xsl:value-of select="a"/></schema:name>
                    <xsl:choose>
                        <xsl:when test="$type='Regi'">
                            <schema:director resource="{$uri}"/>
                        </xsl:when>
                        <xsl:when test="$type='Manus'">
                            <schema:creator resource="{$uri}"/>
                        </xsl:when>
                        <xsl:when test="$type='Producent'">
                            <schema:producer resource="{$uri}"/>
                        </xsl:when>
                        <xsl:when test="$type='Verkställande producent'">
                            <schema:producer resource="{$uri}"/>
                        </xsl:when>
                        <xsl:when test="$type='Klippning'">
                            <schema:editor resource="{$uri}"/>
                        </xsl:when>
                        <xsl:when test="$type='Roll'">
                            <schema:actor resource="{$uri}"/>
                        </xsl:when>
                    </xsl:choose> 
                </rdf:Description>
            </xsl:for-each>
        </xsl:for-each>
    </xsl:template>

    <xsl:template name="remap">
        <xsl:param name="url"/>
        <xsl:choose>
            <xsl:when test="contains($url, 'type=person')">
                <xsl:value-of select="concat($base, 'person/', substring-after($url, 'itemid='))"/>
            </xsl:when>
            <xsl:when test="contains($url, 'type=film')">
                <xsl:value-of select="concat($base, 'movie/', substring-after($url, 'itemid='))"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$url"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>

