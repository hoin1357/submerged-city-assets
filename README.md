# Submerged City Assets

침수 도시 탐험 게임용 Blender·Unity 에셋 보관소입니다.

## 다운로드

3D 원본과 텍스처는 [분류별 백업 폴더](https://github.com/hoin1357/submerged-city-assets/tree/main/assets/packages)에 보관합니다. 각 폴더의 README와 PARTS.json을 참고해 모든 분할 파일을 받은 후 제공된 재결합 도구로 ZIP을 복원하세요. 아직 Releases에는 에셋을 게시하지 않았습니다.

**2026-10-23: 공개 모델·편집 파일 패키지 894종.** 기존 원본 묶음 324종과 추가 건축·가로시설 정리본 458종, 신규 생활용품 6종, 가구·조명 대표 버전 50종과 생활·주방용품 대표 ID 56종을 포함합니다. 50종 중 2종은 보존용 초안이며 나머지도 완성품 인증을 뜻하지 않습니다. 아래 표는 기존 전달본 880종의 목록이며 모든 항목의 업로드 완료를 의미하지 않습니다.

검증된 백업: [A01 구조 126종](https://github.com/hoin1357/submerged-city-assets/tree/main/assets/packages/A01), [A02 비주거 78종](https://github.com/hoin1357/submerged-city-assets/tree/main/assets/packages/A02-nonresidential), [A02 주택 54종](https://github.com/hoin1357/submerged-city-assets/tree/main/assets/packages/A02-residential), [A03 랜드마크 66종](https://github.com/hoin1357/submerged-city-assets/tree/main/assets/packages/A03).

위의 기존 네 묶음은 공개 다운로드 바이트와 원본 SHA-256 일치를 확인했습니다.

추가 공개 정리본: [A04 지붕·옥상 78종](assets/packages/A04), [A05 출입구·창호 90종](assets/packages/A05), [A06 실내 건축 108종](assets/packages/A06), [B01 도로·보도 86종](assets/packages/B01), [B02 가로시설 96종](assets/packages/B02), [신규 생활용품 6종](assets/packages/EVERYDAY), [의자·소파 10종](assets/packages/C001), [가구·조명 40종](assets/packages/FURNITURE40), [생활용품 32개 ID](assets/packages/HOUSEHOLD32), [주방 가전·식기 24개 ID](assets/packages/KITCHEN24). 모델·텍스처와 편집용 Blender 파일을 포함합니다. 경로 및 비시각 메타데이터를 정리했으며 생성 코드·과거 작업 이력·외부 참고 사진은 제외되어 전체 제작 프로젝트의 무손실 백업은 아닙니다. 저장소 Git 객체 해시를 로컬 바이트의 객체 해시와 대조하며, 전체 파일 재다운로드 검증과는 구분합니다.

| 분류 | 고유 에셋 수 |
|---|---:|
| A01 외장 구조·접합 | 126 |
| A02 비주거 건축 | 78 |
| A02 교체 주택 | 54 |
| A03 랜드마크 | 66 |
| A04 지붕 | 78 |
| A05 출입구·창호 | 90 |
| A06 실내 구조 | 108 |
| B01 노면 | 86 |
| B02 가로시설 | 96 |
| B03 교통시설 | 76 |
| B04 승용차 | 12 |
| B04 작업용 차량 | 10 |
| 합계 | 880 |

LOD·충돌 메시·색상 변형은 별도 고유 에셋으로 세지 않습니다. 화물차 10종은 아직 작업 중이며 완료본에 포함하지 않습니다.

## 사용 시 주의

- Blender 원본, FBX 및 함께 제공된 텍스처를 유지하세요.
- Unity에서 재질 연결, 콜라이더 설정, 실제 장면 성능 확인이 별도로 필요합니다. 전체 Unity 런타임 검증이나 출시 준비 완료를 보장하지 않습니다.
- 차량 충돌 메시의 기본 용도는 정적·비볼록 배치입니다. 운전 가능한 동적 차량용 설정은 별도입니다.
- 각 묶음의 설치 안내와 알려진 제한 사항을 먼저 읽으세요.
- 분할 묶음은 해당 백업 폴더에 안내된 모든 필수 파일을 받아야 합니다.

공개 에셋 보관소입니다. 별도의 공개 배포 라이선스는 부여하지 않았습니다.

## 3D 에셋 갤러리

[갤러리 소스](gallery/) · [갤러리 열기](https://hoin1357.github.io/submerged-city-assets/gallery/)

갤러리는 GitHub Pages에서 공개 중입니다. 현재 실제 glTF 연결은 **312종(A01 126/126, A02 비주거 78/78, A02 주거 54/54, A03 48/66, 신규 생활용품 6/6)**입니다. 전체 백업 수량과 3D 미리보기 연결 수량은 다릅니다. WebGL을 지원하는 브라우저가 필요합니다.

한국어 검색·카테고리 탐색, 드래그 회전, 휠/두 손가락 확대, 자동 회전, 시점 초기화와 원본 다운로드를 지원합니다. 실제 모델은 `gallery/manifest.json`의 `assets`에 `id`, `name`, `category`, `src`를 등록합니다. 파일 주소는 manifest 위치 기준이며, 외부 주소는 CORS가 필요합니다. `tags`, `description`, `download`는 선택 항목입니다. glTF는 참조 버퍼와 텍스처를 함께 보관하세요.

뷰어는 Google model-viewer 4.1.0 배포본을 저장소에 포함하며 라이선스는 `gallery/vendor/model-viewer-LICENSE.txt`에 있습니다. 일반 GLB 미리보기에는 별도 서버·API 키·외부 CDN이 필요하지 않습니다. 압축 확장은 추가 디코더가 필요할 수 있습니다. 실제 파일 업로드와 미리보기 검증이 끝난 항목만 연결됩니다.
