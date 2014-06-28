// stdafx.cpp : 標準インクルード depend.pch のみを
// 含むソース ファイルは、プリコンパイル済みヘッダーになります。
// stdafx.obj にはプリコンパイル済み型情報が含まれます。

#include "stdafx.h"

// TODO: このファイルではなく、STDAFX.H で必要な
// 追加ヘッダーを参照してください。

#ifdef __cplusplus
extern "C" {
#endif

extern void exported_function()
{}

extern void exported_function_1()
{}

extern void exported_function_2()
{}

#ifdef __cplusplus
} // extern "C"
#endif
