(async function loadBulkArchive(){
  try {
    const response = await fetch('data/archive.json', { cache: 'no-store' });
    if (!response.ok) return;
    const bulk = await response.json();
    if (!Array.isArray(bulk) || !bulk.length) return;

    for (const ad of bulk) {
      if (typeof ad.image === 'string' && ad.image.startsWith('/ads/')) ad.image = 'public' + ad.image;
      if (!Array.isArray(ad.principles)) ad.principles = [];
      if (!Array.isArray(ad.verificationSources)) ad.verificationSources = [];
      ad.brand = ad.brand || 'Unclassified';
      ad.headline = ad.headline || 'Archive advertisement';
      ad.product = ad.product || 'Historical advertisement';
      ad.hook = ad.hook || 'Not yet independently annotated.';
      ad.offer = ad.offer || 'Not yet independently annotated.';
      ad.proof = ad.proof || 'See the original scan.';
      ad.attribution = ad.attribution || 'medium';
      ad.dateConfidence = ad.dateConfidence || 'low';
      ad.note = ad.note || 'Bulk archive record with exact scan provenance.';
    }

    const existing = new Set(ADS.map(a => a.id));
    ADS.push(...bulk.filter(a => !existing.has(a.id)));
    rebuildFilters();
    render();
  } catch (err) {
    console.warn('Bulk archive manifest is not available yet.', err);
  }
})();
