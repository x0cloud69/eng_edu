
# 📘 MD 파일을 DOC 파일로 변환하는 상세 가이드 (Obsidian용)

---

## 1️⃣ 문서 개요

이 문서는 Obsidian에서 작성한 Markdown(md) 파일을 Microsoft Word(docx) 문서로 변환하면서 다음 요소들을 포함하는 방법을 설명합니다.

- 제목(Title)
- 목차(Table of Contents)
- 페이지 번호(Page Number)
- 깔끔한 문서 스타일

Obsidian에서 바로 열어 사용할 수 있도록 Markdown 형식으로 작성되었습니다.

---

## 2️⃣ 기본 준비 사항

### ✔️ 필요한 도구

- Obsidian
- Pandoc (문서 변환 도구)
- Microsoft Word 또는 호환 프로그램

### ✔️ Pandoc 설치

공식 사이트:

https://pandoc.org

설치 후 터미널 또는 명령 프롬프트에서 아래 명령어로 확인:

```
pandoc --version
```

---

## 3️⃣ MD 파일 구조 만들기 (중요)

DOC 변환 시 목차와 페이지 번호가 제대로 나오려면 Markdown 구조가 중요합니다.

예시:

```
# 문서 제목

## 1. 소개
내용...

## 2. 시스템 개요
내용...

### 2.1 상세 설명
내용...
```

👉 `#`, `##`, `###` 구조가 Word에서 자동 목차가 됩니다.

---

## 4️⃣ 제목(Title) 설정 방법

문서 맨 위에 아래처럼 작성하세요.

```
---
title: "AI Agent 운영 가이드"
author: "작성자 이름"
date: "2026-02-23"
---
```

이 영역을 **YAML Header** 라고 합니다.

DOC 변환 시 표지처럼 사용됩니다.

---

## 5️⃣ 목차(Table of Contents) 자동 생성

Markdown에 아래 구문을 추가하세요.

```
\newpage
# 목차
\tableofcontents
\newpage
```

또는 Pandoc 옵션 사용:

```
--toc
```

---

## 6️⃣ 페이지 번호 자동 추가 방법

Pandoc 변환 시 header 파일을 사용하면 됩니다.

예:

```
pandoc input.md -o output.docx --toc -M page-numbering=true
```

또는 Word 템플릿(reference.docx)을 사용해 기본 스타일을 지정할 수 있습니다.

---

## 7️⃣ 가장 추천하는 변환 명령어 (실무용)

```
pandoc input.md -o output.docx ^
--toc ^
--number-sections ^
--reference-doc=reference.docx
```

설명:

- --toc → 목차 생성
- --number-sections → 자동 번호
- reference-doc → Word 스타일 적용

---

## 8️⃣ Obsidian에서 깔끔하게 보이게 하는 팁

### ✔️ 줄 간격 문제 해결

- Heading 사이에 빈 줄 1개만 유지
- 불필요한 `<br>` 태그 제거

### ✔️ 추천 구조

```
# Title

---

## Chapter 1
내용

## Chapter 2
내용
```

---

## 9️⃣ 실무 Best Practice (Dasom 추천 👍)

- Obsidian에서는 Markdown 구조만 집중
- 디자인은 reference.docx에서 관리
- Heading 레벨을 절대 건너뛰지 말 것

잘 만든 md 구조 = 자동으로 예쁜 Word 문서 생성 🚀

---

## 🔟 요약

1. YAML Header로 제목 만들기
2. Heading 구조로 목차 생성
3. Pandoc 옵션으로 페이지 번호 적용
4. reference.docx로 디자인 통일

이 방식이 현재 가장 안정적인 AI Agent 문서 작성 방식입니다.
