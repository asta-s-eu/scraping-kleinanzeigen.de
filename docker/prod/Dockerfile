ARG ASTA_S_EU_SCRAPING_CORE_VERSION=0.2.3

FROM adan/ciur:${ASTA_S_EU_SCRAPING_CORE_VERSION}

ARG ASTA_S_EU_SCRAPING_KLEINANZEIGEN_DE_VERSION=0.0.2

ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install asta_s_eu_scrapping_kleinanzeigen_de==${ASTA_S_EU_SCRAPING_KLEINANZEIGEN_DE_VERSION} || true

# validate
# RUN set -x && ciur --version | grep -qF "${CIUR_VERSION}"
