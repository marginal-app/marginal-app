from ui.preview import Preview

PREVIEWS = [
    Preview(
        slug="status-ok",
        title="Status / ok",
        description="Success tone — connection saved.",
        component="status",
        group="Primitives",
        kwargs={"message": "연결 성공 — 저장했습니다."},
    ),
    Preview(
        slug="status-error",
        title="Status / error",
        description="Error tone — ping failed.",
        component="status",
        group="Primitives",
        kwargs={
            "tone": "error",
            "message": "연결 실패: 서버가 401로 응답했습니다",
        },
    ),
]
