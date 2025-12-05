"""
범용 CT 이미지 전처리 모듈

학습과 추론 시 동일한 전처리를 적용하여 일관성 보장
인터넷의 임의 CT 이미지도 처리 가능
"""

import numpy as np
import cv2
from PIL import Image
import pydicom
from typing import Union, Tuple, Optional

class CTImagePreprocessor:
    """
    뇌 CT 이미지 전처리 클래스

    - DICOM 및 일반 이미지 형식 지원
    - Window Leveling (뇌 조직 강조)
    - 정규화 및 리사이징
    - 학습/추론 동일 전처리 보장
    """

    def __init__(self,
                 target_size: Tuple[int, int] = (224, 224),
                 apply_windowing: bool = True,
                 brain_window_center: int = 40,
                 brain_window_width: int = 80):
        """
        Args:
            target_size: 출력 이미지 크기 (height, width)
            apply_windowing: Window Leveling 적용 여부
            brain_window_center: Brain window center (HU)
            brain_window_width: Brain window width (HU)
        """
        self.target_size = target_size
        self.apply_windowing = apply_windowing
        self.window_center = brain_window_center
        self.window_width = brain_window_width

    def load_image(self, image_path: str) -> np.ndarray:
        """
        이미지 파일 로드 (DICOM 또는 일반 이미지)

        Args:
            image_path: 이미지 파일 경로

        Returns:
            numpy array (height, width) 또는 (height, width, channels)
        """
        try:
            # DICOM 형식 시도
            if image_path.lower().endswith('.dcm'):
                dcm = pydicom.dcmread(image_path)
                image = dcm.pixel_array
                return image
        except:
            pass

        # 일반 이미지 형식 (JPG, PNG 등)
        try:
            image = Image.open(image_path)
            image = np.array(image)
            return image
        except Exception as e:
            raise ValueError(f"이미지 로드 실패: {e}")

    def apply_brain_windowing(self, image: np.ndarray) -> np.ndarray:
        """
        Brain Window Leveling 적용
        뇌 조직의 밀도 범위를 강조

        Args:
            image: 입력 이미지 (Hounsfield Units 또는 일반 픽셀값)

        Returns:
            Windowed image (0-255 범위로 정규화)
        """
        img_min = self.window_center - self.window_width // 2
        img_max = self.window_center + self.window_width // 2

        # Windowing 적용
        windowed = np.clip(image, img_min, img_max)

        # 0-255 범위로 정규화
        windowed = ((windowed - img_min) / (img_max - img_min) * 255).astype(np.uint8)

        return windowed

    def normalize_ct_image(self, image: np.ndarray) -> np.ndarray:
        """
        CT 이미지 정규화

        Args:
            image: 입력 이미지

        Returns:
            정규화된 이미지 (0-255 uint8)
        """
        # 이미 uint8이면 그대로 반환
        if image.dtype == np.uint8:
            return image

        # float이거나 다른 타입이면 정규화
        img_min = image.min()
        img_max = image.max()

        if img_max - img_min == 0:
            return np.zeros_like(image, dtype=np.uint8)

        normalized = ((image - img_min) / (img_max - img_min) * 255).astype(np.uint8)
        return normalized

    def convert_to_rgb(self, image: np.ndarray) -> np.ndarray:
        """
        그레이스케일 이미지를 RGB로 변환

        Args:
            image: 입력 이미지 (H, W) 또는 (H, W, C)

        Returns:
            RGB 이미지 (H, W, 3)
        """
        if len(image.shape) == 2:
            # 그레이스케일 → RGB
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif len(image.shape) == 3:
            if image.shape[2] == 1:
                # (H, W, 1) → RGB
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                # RGBA → RGB
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            # 이미 RGB면 그대로 유지

        return image

    def resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        이미지 리사이징

        Args:
            image: 입력 이미지

        Returns:
            리사이즈된 이미지
        """
        resized = cv2.resize(image, self.target_size, interpolation=cv2.INTER_AREA)
        return resized

    def validate_ct_image(self, image: np.ndarray) -> Tuple[bool, str]:
        """
        CT 이미지 유효성 검증

        Args:
            image: 입력 이미지

        Returns:
            (is_valid, message)
        """
        # 크기 확인
        if image.size == 0:
            return False, "이미지가 비어있습니다."

        # 최소 크기 확인 (너무 작은 이미지 거부)
        if image.shape[0] < 64 or image.shape[1] < 64:
            return False, f"이미지가 너무 작습니다 ({image.shape[0]}x{image.shape[1]}). 최소 64x64 필요."

        # 최대 크기 확인
        if image.shape[0] > 4096 or image.shape[1] > 4096:
            return False, f"이미지가 너무 큽니다 ({image.shape[0]}x{image.shape[1]}). 최대 4096x4096."

        return True, "유효한 이미지입니다."

    def preprocess(self, image_path: str,
                   return_original: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        전체 전처리 파이프라인 실행

        Args:
            image_path: 이미지 파일 경로
            return_original: True면 (전처리 이미지, 원본 이미지) 반환

        Returns:
            전처리된 이미지 (1, H, W, 3) - 모델 입력 ready
            또는 (전처리 이미지, 원본 이미지) if return_original=True
        """
        # 1. 이미지 로드
        image = self.load_image(image_path)
        original = image.copy()

        # 2. 유효성 검증
        is_valid, message = self.validate_ct_image(image)
        if not is_valid:
            raise ValueError(f"이미지 검증 실패: {message}")

        # 3. Window Leveling (선택적)
        if self.apply_windowing and image.dtype != np.uint8:
            # DICOM 이미지는 windowing 적용
            image = self.apply_brain_windowing(image)
        else:
            # 일반 이미지는 정규화
            image = self.normalize_ct_image(image)

        # 4. RGB 변환
        image = self.convert_to_rgb(image)

        # 5. 리사이징
        image = self.resize_image(image)

        # 6. 정규화 (0-1 범위)
        image = image.astype(np.float32) / 255.0

        # 7. 배치 차원 추가 (모델 입력 형식)
        image = np.expand_dims(image, axis=0)

        if return_original:
            return image, original
        return image


# ============================================================
# 간단한 사용 예시 함수
# ============================================================

def preprocess_for_prediction(image_path: str,
                              target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    예측용 이미지 전처리 (간단한 인터페이스)

    Args:
        image_path: 이미지 파일 경로
        target_size: 출력 크기

    Returns:
        전처리된 이미지 (1, H, W, 3)
    """
    preprocessor = CTImagePreprocessor(target_size=target_size)
    return preprocessor.preprocess(image_path)


def preprocess_for_visualization(image_path: str,
                                 target_size: Tuple[int, int] = (224, 224)) -> Tuple[np.ndarray, np.ndarray]:
    """
    시각화용 전처리 (전처리 이미지 + 원본)

    Args:
        image_path: 이미지 파일 경로
        target_size: 출력 크기

    Returns:
        (전처리 이미지, 원본 이미지)
    """
    preprocessor = CTImagePreprocessor(target_size=target_size)
    return preprocessor.preprocess(image_path, return_original=True)


# ============================================================
# Test-Time Augmentation (TTA) 함수
# ============================================================

def predict_with_tta(model, image_path: str,
                    target_size: Tuple[int, int] = (224, 224),
                    num_augmentations: int = 5) -> float:
    """
    Test-Time Augmentation을 사용한 robust 예측

    여러 augmentation 버전으로 예측 후 평균하여 더 안정적인 결과 생성

    Args:
        model: 학습된 Keras 모델
        image_path: 이미지 파일 경로
        target_size: 이미지 크기
        num_augmentations: Augmentation 횟수

    Returns:
        평균 예측 확률
    """
    preprocessor = CTImagePreprocessor(target_size=target_size)
    image = preprocessor.load_image(image_path)

    predictions = []

    # 원본 이미지 예측
    img_preprocessed = preprocessor.preprocess(image_path)
    pred = model.predict(img_preprocessed, verbose=0)[0][0]
    predictions.append(pred)

    # Augmented 버전들 예측
    for i in range(num_augmentations - 1):
        # 랜덤 augmentation 적용
        augmented = image.copy()

        # Horizontal flip (50% 확률)
        if np.random.rand() > 0.5:
            augmented = cv2.flip(augmented, 1)

        # 작은 rotation (-5 ~ 5도)
        if np.random.rand() > 0.5:
            angle = np.random.uniform(-5, 5)
            h, w = augmented.shape[:2]
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
            augmented = cv2.warpAffine(augmented, M, (w, h))

        # 전처리 후 예측
        augmented = preprocessor.normalize_ct_image(augmented)
        augmented = preprocessor.convert_to_rgb(augmented)
        augmented = preprocessor.resize_image(augmented)
        augmented = augmented.astype(np.float32) / 255.0
        augmented = np.expand_dims(augmented, axis=0)

        pred = model.predict(augmented, verbose=0)[0][0]
        predictions.append(pred)

    # 평균 반환
    return np.mean(predictions)


if __name__ == "__main__":
    # 테스트 코드
    print("CT Image Preprocessor 모듈")
    print("사용 예시:")
    print("  preprocessor = CTImagePreprocessor(target_size=(224, 224))")
    print("  image = preprocessor.preprocess('path/to/ct_image.jpg')")
    print("  prediction = model.predict(image)")
