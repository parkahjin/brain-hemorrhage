"""
Grad-CAM (Gradient-weighted Class Activation Mapping) 구현

모델이 어느 부위를 보고 판단했는지 시각화
뇌출혈 진단의 근거를 제시
"""

import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
from typing import Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.cm as cm


class GradCAM:
    """
    Grad-CAM 구현 클래스

    ResNet50 등 CNN 모델에서 마지막 Conv layer의 activation을 추출하여
    어느 영역이 예측에 중요한지 히트맵으로 시각화
    """

    def __init__(self, model: keras.Model, layer_name: Optional[str] = None):
        """
        Args:
            model: 학습된 Keras 모델
            layer_name: Grad-CAM을 적용할 레이어 이름
                       None이면 마지막 Conv layer 자동 탐색
        """
        self.model = model

        # 마지막 Conv layer 찾기
        if layer_name is None:
            layer_name = self._find_last_conv_layer()

        self.layer_name = layer_name
        print(f"Grad-CAM 적용 레이어: {layer_name}")

    def _find_last_conv_layer(self) -> str:
        """
        모델에서 마지막 Convolutional layer 찾기

        Returns:
            마지막 Conv layer의 이름
        """
        for layer in reversed(self.model.layers):
            # Conv2D 레이어 찾기
            try:
                if hasattr(layer, 'output_shape') and len(layer.output_shape) == 4:  # (None, H, W, C)
                    return layer.name
                # Functional API 모델인 경우
                elif hasattr(layer, 'output') and hasattr(layer.output, 'shape'):
                    if len(layer.output.shape) == 4:
                        return layer.name
            except:
                continue

        raise ValueError("모델에서 Convolutional layer를 찾을 수 없습니다.")

    def generate_heatmap(self,
                        image: np.ndarray,
                        pred_index: Optional[int] = None) -> np.ndarray:
        """
        Grad-CAM 히트맵 생성

        Args:
            image: 전처리된 이미지 (1, H, W, 3)
            pred_index: 예측 클래스 인덱스 (None이면 예측된 클래스 사용)

        Returns:
            히트맵 (0-1 범위, H, W)
        """
        # Gradient 계산을 위한 서브모델 생성
        grad_model = keras.models.Model(
            inputs=[self.model.inputs],
            outputs=[self.model.get_layer(self.layer_name).output,
                    self.model.output]
        )

        # Gradient 계산
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(image)

            # Binary classification인 경우
            if pred_index is None:
                pred_index = 0  # sigmoid output

            # 예측값 추출
            if predictions.shape[-1] == 1:
                # Binary classification (sigmoid)
                class_channel = predictions[:, 0]
            else:
                # Multi-class (softmax)
                class_channel = predictions[:, pred_index]

        # Gradient 계산
        grads = tape.gradient(class_channel, conv_outputs)

        # Global Average Pooling on gradients
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # Conv outputs와 pooled gradients를 곱하여 중요도 가중치 적용
        conv_outputs = conv_outputs[0]
        pooled_grads = pooled_grads.numpy()
        conv_outputs = conv_outputs.numpy()

        for i in range(len(pooled_grads)):
            conv_outputs[:, :, i] *= pooled_grads[i]

        # Channel-wise sum
        heatmap = np.sum(conv_outputs, axis=-1)

        # ReLU 적용 (양수만 유지)
        heatmap = np.maximum(heatmap, 0)

        # 0-1 정규화
        if heatmap.max() > 0:
            heatmap /= heatmap.max()

        return heatmap

    def overlay_heatmap(self,
                       heatmap: np.ndarray,
                       original_image: np.ndarray,
                       alpha: float = 0.4,
                       colormap: int = cv2.COLORMAP_JET) -> np.ndarray:
        """
        히트맵을 원본 이미지에 오버레이

        Args:
            heatmap: Grad-CAM 히트맵 (0-1 범위)
            original_image: 원본 이미지 (H, W) or (H, W, 3)
            alpha: 투명도 (0: 원본만, 1: 히트맵만)
            colormap: OpenCV 컬러맵

        Returns:
            오버레이된 이미지 (H, W, 3)
        """
        # 원본 이미지 크기로 히트맵 리사이즈
        if len(original_image.shape) == 2:
            h, w = original_image.shape
        else:
            h, w = original_image.shape[:2]

        heatmap_resized = cv2.resize(heatmap, (w, h))

        # 히트맵을 0-255로 변환
        heatmap_uint8 = np.uint8(255 * heatmap_resized)

        # 컬러맵 적용
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, colormap)

        # 원본 이미지를 RGB로 변환 및 정규화
        if len(original_image.shape) == 2:
            original_rgb = cv2.cvtColor(original_image, cv2.COLOR_GRAY2RGB)
        else:
            original_rgb = original_image.copy()

        # 원본 이미지가 float이면 uint8로 변환
        if original_rgb.dtype != np.uint8:
            if original_rgb.max() <= 1.0:
                original_rgb = (original_rgb * 255).astype(np.uint8)
            else:
                original_rgb = original_rgb.astype(np.uint8)

        # 오버레이
        overlayed = cv2.addWeighted(original_rgb, 1 - alpha, heatmap_colored, alpha, 0)

        return overlayed

    def explain_prediction(self,
                          image_path: str,
                          preprocessor,
                          threshold: float = 0.5) -> dict:
        """
        예측 결과를 Grad-CAM으로 설명

        Args:
            image_path: 이미지 파일 경로
            preprocessor: CTImagePreprocessor 인스턴스
            threshold: Binary classification threshold

        Returns:
            dict with keys: prediction, heatmap, overlay, explanation
        """
        # 이미지 전처리
        preprocessed_image, original_image = preprocessor.preprocess(
            image_path, return_original=True
        )

        # 예측
        prediction = self.model.predict(preprocessed_image, verbose=0)[0][0]
        predicted_class = "hemorrhage" if prediction >= threshold else "normal"

        # Grad-CAM 히트맵 생성
        heatmap = self.generate_heatmap(preprocessed_image)

        # 오버레이 생성
        overlay = self.overlay_heatmap(heatmap, original_image, alpha=0.4)

        # 설명 텍스트 생성
        explanation = self._generate_explanation_text(
            heatmap, prediction, predicted_class
        )

        return {
            'prediction': prediction,
            'predicted_class': predicted_class,
            'confidence': prediction if prediction >= 0.5 else 1 - prediction,
            'heatmap': heatmap,
            'overlay': overlay,
            'original': original_image,
            'explanation': explanation
        }

    def _generate_explanation_text(self,
                                   heatmap: np.ndarray,
                                   prediction: float,
                                   predicted_class: str) -> str:
        """
        히트맵 기반 설명 텍스트 생성

        Args:
            heatmap: Grad-CAM 히트맵
            prediction: 예측 확률
            predicted_class: 예측 클래스

        Returns:
            설명 텍스트
        """
        # 히트맵에서 최대 활성화 영역 찾기
        max_activation = heatmap.max()
        threshold = 0.7 * max_activation  # 상위 30% 활성화 영역

        # 활성화 영역의 중심점 계산
        high_activation_mask = (heatmap >= threshold).astype(np.uint8)
        y_coords, x_coords = np.where(high_activation_mask > 0)

        if len(y_coords) > 0:
            center_y = int(np.mean(y_coords))
            center_x = int(np.mean(x_coords))

            # 뇌 영역 추정 (간단한 4분면 분할)
            h, w = heatmap.shape
            region = self._localize_brain_region(center_x, center_y, w, h)
        else:
            region = "전체 영역"

        # 신뢰도
        confidence = prediction if prediction >= 0.5 else 1 - prediction

        # 설명 텍스트 구성
        if predicted_class == "hemorrhage":
            explanation = f"""
**진단 결과: 뇌출혈 의심**

- **신뢰도**: {confidence*100:.1f}%
- **주요 관심 영역**: {region}
- **분석**: 빨간색으로 표시된 부위에서 고밀도 영역이 감지되었습니다. \
이는 뇌출혈의 특징적인 패턴과 유사합니다.

⚠️ **주의**: 이 결과는 보조 진단 도구로만 사용되어야 하며, \
전문의의 최종 판단을 대체할 수 없습니다.
            """.strip()
        else:
            explanation = f"""
**진단 결과: 정상**

- **신뢰도**: {confidence*100:.1f}%
- **분석**: 뇌출혈을 시사하는 특이 소견이 발견되지 않았습니다.

✅ **참고**: 정상 소견이지만, 임상 증상이 있다면 전문의 상담을 권장합니다.
            """.strip()

        return explanation

    def _localize_brain_region(self,
                               x: int, y: int,
                               width: int, height: int) -> str:
        """
        뇌 영역 추정 (간단한 4분면 + 중앙)

        Args:
            x, y: 중심 좌표
            width, height: 이미지 크기

        Returns:
            영역 설명
        """
        # 9분면으로 나누기
        w_third = width / 3
        h_third = height / 3

        # 좌우 구분
        if x < w_third:
            lr = "좌측"
        elif x > 2 * w_third:
            lr = "우측"
        else:
            lr = "중앙"

        # 상하 구분
        if y < h_third:
            tb = "상부"
        elif y > 2 * h_third:
            tb = "하부"
        else:
            tb = "중간부"

        # 영역 매핑 (간단한 버전)
        region_map = {
            ("좌측", "상부"): "좌측 전두엽",
            ("중앙", "상부"): "전두엽 중앙",
            ("우측", "상부"): "우측 전두엽",
            ("좌측", "중간부"): "좌측 측두엽/두정엽",
            ("중앙", "중간부"): "기저핵/시상",
            ("우측", "중간부"): "우측 측두엽/두정엽",
            ("좌측", "하부"): "좌측 후두엽/소뇌",
            ("중앙", "하부"): "뇌간/소뇌",
            ("우측", "하부"): "우측 후두엽/소뇌",
        }

        return region_map.get((lr, tb), f"{lr} {tb}")


def visualize_gradcam(result: dict, figsize: Tuple[int, int] = (15, 5)):
    """
    Grad-CAM 결과 시각화

    Args:
        result: GradCAM.explain_prediction() 결과
        figsize: Figure 크기
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)

    # 원본 이미지
    axes[0].imshow(result['original'], cmap='gray' if len(result['original'].shape) == 2 else None)
    axes[0].set_title('Original Image')
    axes[0].axis('off')

    # 히트맵
    axes[1].imshow(result['heatmap'], cmap='jet')
    axes[1].set_title('Grad-CAM Heatmap')
    axes[1].axis('off')

    # 오버레이
    axes[2].imshow(result['overlay'])
    axes[2].set_title(f"Prediction: {result['predicted_class']} ({result['confidence']*100:.1f}%)")
    axes[2].axis('off')

    plt.tight_layout()
    plt.show()

    # 설명 출력
    print("\n" + "="*60)
    print(result['explanation'])
    print("="*60)


# ============================================================
# 간편 사용 함수
# ============================================================

def explain_with_gradcam(model: keras.Model,
                        image_path: str,
                        preprocessor,
                        save_path: Optional[str] = None) -> dict:
    """
    Grad-CAM을 사용하여 예측 설명 (간편 인터페이스)

    Args:
        model: 학습된 모델
        image_path: 이미지 경로
        preprocessor: CTImagePreprocessor 인스턴스
        save_path: 결과 저장 경로 (None이면 저장 안함)

    Returns:
        설명 결과 dict
    """
    gradcam = GradCAM(model)
    result = gradcam.explain_prediction(image_path, preprocessor)

    # 시각화
    visualize_gradcam(result)

    # 저장
    if save_path:
        cv2.imwrite(save_path, cv2.cvtColor(result['overlay'], cv2.COLOR_RGB2BGR))
        print(f"\n💾 결과 저장: {save_path}")

    return result


if __name__ == "__main__":
    print("Grad-CAM 모듈")
    print("사용 예시:")
    print("  from gradcam_utils import GradCAM, explain_with_gradcam")
    print("  from preprocessing_utils import CTImagePreprocessor")
    print()
    print("  preprocessor = CTImagePreprocessor()")
    print("  result = explain_with_gradcam(model, 'image.jpg', preprocessor)")
