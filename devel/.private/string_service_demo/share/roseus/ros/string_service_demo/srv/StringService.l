;; Auto-generated. Do not edit!


(when (boundp 'string_service_demo::StringService)
  (if (not (find-package "STRING_SERVICE_DEMO"))
    (make-package "STRING_SERVICE_DEMO"))
  (shadow 'StringService (find-package "STRING_SERVICE_DEMO")))
(unless (find-package "STRING_SERVICE_DEMO::STRINGSERVICE")
  (make-package "STRING_SERVICE_DEMO::STRINGSERVICE"))
(unless (find-package "STRING_SERVICE_DEMO::STRINGSERVICEREQUEST")
  (make-package "STRING_SERVICE_DEMO::STRINGSERVICEREQUEST"))
(unless (find-package "STRING_SERVICE_DEMO::STRINGSERVICERESPONSE")
  (make-package "STRING_SERVICE_DEMO::STRINGSERVICERESPONSE"))

(in-package "ROS")





(defclass string_service_demo::StringServiceRequest
  :super ros::object
  :slots (_data ))

(defmethod string_service_demo::StringServiceRequest
  (:init
   (&key
    ((:data __data) "")
    )
   (send-super :init)
   (setq _data (string __data))
   self)
  (:data
   (&optional __data)
   (if __data (setq _data __data)) _data)
  (:serialization-length
   ()
   (+
    ;; string _data
    4 (length _data)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _data
       (write-long (length _data) s) (princ _data s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _data
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _data (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(defclass string_service_demo::StringServiceResponse
  :super ros::object
  :slots (_result ))

(defmethod string_service_demo::StringServiceResponse
  (:init
   (&key
    ((:result __result) "")
    )
   (send-super :init)
   (setq _result (string __result))
   self)
  (:result
   (&optional __result)
   (if __result (setq _result __result)) _result)
  (:serialization-length
   ()
   (+
    ;; string _result
    4 (length _result)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _result
       (write-long (length _result) s) (princ _result s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _result
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _result (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(defclass string_service_demo::StringService
  :super ros::object
  :slots ())

(setf (get string_service_demo::StringService :md5sum-) "7229f1b0de733d7956dd646adcbf7e06")
(setf (get string_service_demo::StringService :datatype-) "string_service_demo/StringService")
(setf (get string_service_demo::StringService :request) string_service_demo::StringServiceRequest)
(setf (get string_service_demo::StringService :response) string_service_demo::StringServiceResponse)

(defmethod string_service_demo::StringServiceRequest
  (:response () (instance string_service_demo::StringServiceResponse :init)))

(setf (get string_service_demo::StringServiceRequest :md5sum-) "7229f1b0de733d7956dd646adcbf7e06")
(setf (get string_service_demo::StringServiceRequest :datatype-) "string_service_demo/StringServiceRequest")
(setf (get string_service_demo::StringServiceRequest :definition-)
      "string data
---
string result
")

(setf (get string_service_demo::StringServiceResponse :md5sum-) "7229f1b0de733d7956dd646adcbf7e06")
(setf (get string_service_demo::StringServiceResponse :datatype-) "string_service_demo/StringServiceResponse")
(setf (get string_service_demo::StringServiceResponse :definition-)
      "string data
---
string result
")



(provide :string_service_demo/StringService "7229f1b0de733d7956dd646adcbf7e06")


