# 생성될 리소스

- **OpenSearchSecret**: OpenSearch 사용자명과 비밀번호를 저장하는 AWS Secrets Manager 시크릿.
- **CodeRepository**: OpenSearch 워크숍을 위한 코드를 \호스팅하는 AWS SageMaker 코드 리포지토리.
- **NotebookInstance**: 코드 리포지토리를 사용하는 AWS SageMaker 노트북 인스턴스.
- **NBRole**: SageMaker 노트북 인스턴스에 필요한 권한을 부여하는 IAM 역할.
- **LambdaIAMRole**: Lambda 함수에 필요한 권한을 부여하는 IAM 역할.
- **Role**: SageMaker 환경에 필요한 권한을 부여하는 IAM 역할.
- **s3BucketTraining**: 학습 데이터를 저장하는 S3 버킷.
- **s3BucketHosting**: 프론트엔드 애플리케이션을 호스팅하는 S3 버킷.
- **OpenSearchServiceDomain**: OpenSearch 클러스터를 호스팅하는 Amazon OpenSearch Service 도메인.

# 환경 구성

## CloudFormation

### CloudFormation 파일 다운로드

[`opensearch_setup_small.yaml`](https://github.com/atheanchu/opensearch-workshop-kor/blob/main/00.Setup/semantic-search_small.yaml) 파일을 다운로드 받습니다.

### CloudFormation 배포

다음 명령어를 실행하여 `opensearch_setup_small.yaml` 파일을 배포합니다. 이 워크샵에서는 이후 Amazon Bedrock과의 연계를 위해 `us-east-1` 지역에 배포합니다. 완료되는데 15분에서 20분 정도 소요됩니다.

```
aws cloudformation create-stack \
  --stack-name opensearch-workshop \
  --region us-east-1 \
  --template-body file://00.Setup/opensearch_setup_small.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

# Nori 텍스트 분석기 패키지 설치

시간은 약 30분 정도 소요됩니다.다음 명령어를 수행하여 nori 텍스트 분석기를 도메인에 설치합니다. G181660338는 us-east-1 리전의 analysis-nori의 패키지 ID입니다. 

```
aws opensearch associate-package \
  --domain-name opensearch-workshop \
  --region us-east-1 \
  --package-id G181660338
```

# Amazon Bedrock 모델 접근 권한 얻기

## 사용할 모델

- Amazon Titan Embeddings G1 - Text
- Titan Multimodal Embeddings G1
- Cohere Embed Multilingual
- Anthropic Claude 3 Haiku

## 접근 권한 신청하기

Amazon Bedrock 의 왼쪽 아래 [Model Access](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess) 메뉴에서 다음 모델에 대한 권한을 신청합니다. 

![Requesting Model Access](images/image.png)

### 축하합니다. 이제 워크샵을 할 준비가 끝났습니다.