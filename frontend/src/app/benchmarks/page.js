'use client';

import '../i18n';
import { useTranslation } from 'react-i18next';
import Link from 'next/link';

const categories = [
  {
    key: 'benchmarks_category_sentiment',
    benchmarks: [
      { titleKey: 'benchmark_alloCine_title', descKey: 'benchmark_alloCine_description', link: 'https://huggingface.co/datasets/CATIE-AQ/allocine_fr_prompt_sentiment_analysis', metrics: 'Accuracy' },
      { titleKey: 'benchmark_mms_title', descKey: 'benchmark_mms_description', link: 'https://huggingface.co/datasets/Brand24/mms', metrics: 'Accuracy' },
    ],
  },
  {
    key: 'benchmarks_category_nli',
    benchmarks: [
      { titleKey: 'benchmark_fracas_title', descKey: 'benchmark_fracas_description', link: 'https://huggingface.co/datasets/maximoss/fracas', metrics: 'Accuracy' },
      { titleKey: 'benchmark_gqnli_title', descKey: 'benchmark_gqnli_description', link: 'https://huggingface.co/datasets/maximoss/gqnli-fr', metrics: 'Accuracy' },
      { titleKey: 'benchmark_lingnli_title', descKey: 'benchmark_lingnli_description', link: 'https://huggingface.co/datasets/maximoss/lingnli-multi-mt', metrics: 'Accuracy' },
      { titleKey: 'benchmark_mnli_nineeleven_fr_mt_title', descKey: 'benchmark_mnli_nineeleven_fr_mt_description', link: 'https://huggingface.co/datasets/maximoss/mnli-nineeleven-fr-mt', metrics: 'Accuracy' },
      { titleKey: 'benchmark_rte3_french_title', descKey: 'benchmark_rte3_french_description', link: 'https://huggingface.co/datasets/maximoss/rte3-french', metrics: 'Accuracy' },
      { titleKey: 'benchmark_sickfr_title', descKey: 'benchmark_sickfr_description', link: 'https://huggingface.co/datasets/Lajavaness/SICK-fr', metrics: 'Pearson' },
      { titleKey: 'benchmark_xnli_title', descKey: 'benchmark_xnli_description', link: 'https://github.com/facebookresearch/XNLI', metrics: 'Accuracy' },
      { titleKey: 'benchmark_daccord_title', descKey: 'benchmark_daccord_description', link: 'https://huggingface.co/datasets/maximoss/daccord-contradictions', metrics: 'Accuracy' },
    ],
  },
  {
    key: 'benchmarks_category_qa',
    benchmarks: [
      { titleKey: 'benchmark_fquad_title', descKey: 'benchmark_fquad_description', link: 'https://arxiv.org/pdf/2002.06071', metrics: 'F1 Score, Exact Match Ratio' },
      { titleKey: 'benchmark_french_boolq_title', descKey: 'benchmark_french_boolq_description', link: 'https://huggingface.co/datasets/manu/french_boolq', metrics: 'Accuracy' },
      { titleKey: 'benchmark_piaf_title', descKey: 'benchmark_piaf_description', link: 'https://aclanthology.org/2020.lrec-1.673/', metrics: 'F1 Score, Exact Match Ratio' },
    ],
  },
  {
    key: 'benchmarks_category_paraphrase',
    benchmarks: [
      { titleKey: 'benchmark_paws_title', descKey: 'benchmark_paws_description', link: 'https://huggingface.co/datasets/google-research-datasets/paws-x', metrics: 'Accuracy' },
      { titleKey: 'benchmark_qfrblimp_title', descKey: 'benchmark_qfrblimp_description', link: 'https://github.com/davebulaval/FrBLiMP', metrics: 'Accuracy' },
    ],
  },
  {
    key: 'benchmarks_category_grammar',
    benchmarks: [
      { titleKey: 'benchmark_multiblimp_title', descKey: 'benchmark_multiblimp_description', link: 'https://huggingface.co/datasets/jumelet/multiblimp', metrics: 'Accuracy' },
      { titleKey: 'benchmark_qfrcola_title', descKey: 'benchmark_qfrcola_description', link: 'https://github.com/davebulaval/qfrcola', metrics: 'Accuracy' },
    ],
  },
  {
    key: 'benchmarks_category_similarity',
    benchmarks: [
      { titleKey: 'benchmark_sts22_title', descKey: 'benchmark_sts22_description', link: 'https://huggingface.co/datasets/mteb/sts22-crosslingual-sts/viewer/fr', metrics: 'Pearson' },
    ],
  },
  {
    key: 'benchmarks_category_wsd',
    benchmarks: [
      { titleKey: 'benchmark_wsd_title', descKey: 'benchmark_wsd_description', link: 'https://huggingface.co/datasets/GETALP/flue', metrics: 'Exact Match Ratio' },
    ],
  },
  {
    key: 'benchmarks_category_quebec',
    benchmarks: [
      { titleKey: 'benchmark_qfrcore_title', descKey: 'benchmark_qfrcore_description', link: '', metrics: 'Accuracy' },
      { titleKey: 'benchmark_qfrcort_title', descKey: 'benchmark_qfrcort_description', link: '', metrics: 'Accuracy' },
    ],
  },
  {
    key: 'benchmarks_category_coreference',
    benchmarks: [
      { titleKey: 'benchmark_wino_x_lm_title', descKey: 'benchmark_wino_x_lm_description', link: 'https://huggingface.co/datasets/demelin/wino_x/viewer/lm_en_fr?views%5B%5D=lm_en_fr', metrics: 'Accuracy' },
      { titleKey: 'benchmark_wino_x_mt_title', descKey: 'benchmark_wino_x_mt_description', link: 'https://huggingface.co/datasets/demelin/wino_x/viewer/mt_en_fr', metrics: 'Accuracy' },
    ],
  },
];

export default function Benchmarks() {
  const { t } = useTranslation();

  return (
    <div suppressHydrationWarning>
      <div className="max-w-3xl mx-auto px-2 py-3">
        <p className="text-1.5xl text-left text-gray-800">
          {t('benchmarksIntro')}
        </p>
      </div>
      <div className="space-y-10">
        {categories.map((cat) => (
          <div key={cat.key}>
            <h2 className="text-xl font-bold text-blue-700 mb-4 border-l-4 border-blue-600 pl-3">
              {t(cat.key)}
            </h2>
            <div className="space-y-4">
              {cat.benchmarks.map((b) => (
                <Benchmark
                  key={b.titleKey}
                  title={t(b.titleKey)}
                  link={b.link}
                  description={t(b.descKey)}
                  metrics={b.metrics}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Benchmark({ title, description, metrics, link }) {
  const { t } = useTranslation();

  return (
    <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h3 className="text-xl font-semibold text-blue-700 mb-2 border-b-2 border-blue-500 inline-block">
        {link ? (
          <Link href={link} className="hover:underline">
            {title}
          </Link>
        ) : (
          title
        )}
      </h3>
      <p className="text-gray-700 mb-2">{description}</p>
      <p className="text-sm text-gray-500">
        <span className="font-medium">{t('metrics')}</span> {metrics}
      </p>
    </div>
  );
}
