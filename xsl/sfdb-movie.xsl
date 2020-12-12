<?xml version="1.0"?> 
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:schema="https://schema.org/">
    <xsl:param name="uri"/>
    <xsl:param name="base">https://id.svenskfilmdatabas.se/</xsl:param>

    <xsl:template match="/">
		<rdf:RDF>
            <rdf:Description rdf:about="{$uri}">
			    <xsl:apply-templates select="//h2[@id='titles']"/>
			    <xsl:apply-templates select="//h2[@id='crew']"/>
			    <xsl:apply-templates select="//h2[@id='cast']"/>
                <xsl:apply-templates select="//h2[@id='plot-summary']"/>
            </rdf:Description>
		</rdf:RDF>
	</xsl:template>

    <xsl:template match="h2[@id='titles']">
        <xsl:for-each select="following-sibling::div[1]/div/table/tbody/tr">
            <xsl:variable name="type" select="th"/>
            <xsl:for-each select="td/ul/li">
                <xsl:choose>
                    <xsl:when test="$type='Internationell titel'">
                        <schema:name><xsl:value-of select="."/></schema:name>
                    </xsl:when>
                    <xsl:when test="$type='Originaltitel'">
                        <schema:name><xsl:value-of select="."/></schema:name>
                    </xsl:when>
                    <xsl:when test="$type='Svensk premiärtitel'">
                        <schema:name><xsl:value-of select="."/></schema:name>
                    </xsl:when>
                </xsl:choose> 
            </xsl:for-each>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="h2[@id='plot-summary']">
        <schema:abstract>
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
        </schema:abstract>
    </xsl:template>

    <xsl:template match="h2[@id='crew']">
        <xsl:for-each select="following-sibling::div[1]/div/table/tbody/tr">
            <xsl:variable name="predicate">
                <xsl:choose>
                    <xsl:when test="th='Regi'">director</xsl:when>
                    <xsl:when test="th='Manus'">creator</xsl:when>
                    <xsl:when test="th='Producent'">producer</xsl:when>
                </xsl:choose>
            </xsl:variable>
            <xsl:if test="$predicate!=''">
                <xsl:for-each select="td/ul/li">
                    <xsl:element name="{$predicate}" namespace="https://schema.org/">
                        <rdf:Description>
                            <xsl:if test="a">
                                <xsl:attribute name="about" namespace="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                                    <xsl:call-template name="remap">
                                        <xsl:with-param name="url" select="a/@href"/>
                                    </xsl:call-template>
                                </xsl:attribute>
                            </xsl:if>
                            <rdf:type resource="https://schema.org/Person"/>
                            <schema:name><xsl:value-of select="."/></schema:name>
                        </rdf:Description>
                    </xsl:element>
                </xsl:for-each>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="h2[@id='cast']">
        <xsl:for-each select="following-sibling::div[1]/div/table/tbody/tr">
            <schema:actor>
                <rdf:Description>
                    <xsl:if test="td/a">
                        <xsl:attribute name="about" namespace="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                            <xsl:call-template name="remap">
                                <xsl:with-param name="url" select="td/a/@href"/>
                            </xsl:call-template>
                        </xsl:attribute>
                    </xsl:if>
                    <rdf:type resource="https://schema.org/Person"/>
                    <schema:name><xsl:value-of select="td"/></schema:name>
                </rdf:Description>
            </schema:actor>
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

