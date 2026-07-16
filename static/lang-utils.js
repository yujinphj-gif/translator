export const languageOptions = [
    { value: 'ko', label: '한국어', translateKey: 'ko' },
    { value: 'en', label: '영어', translateKey: 'en' },
    { value: 'tl', label: '필리핀어', translateKey: 'tl' },
    { value: 'id', label: '인도네시아어', translateKey: 'id' },
    { value: 'vi', label: '베트남어', translateKey: 'vi' }
];

export function getLanguageLabel(code) {
    const option = languageOptions.find(opt => opt.value === code);
    return option ? option.label : code;
}
